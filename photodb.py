from pillow_heif import register_heif_opener
from flask import Flask, jsonify
from openai import OpenAI
from pathlib import Path
from io import BytesIO
from PIL import Image
import subprocess
import datetime
import sqlite3
import base64
import json
import yaml
import sys
import os

from config import *


class PhotoDB:

    # ---------------
    # Data structures
    # ---------------

    con = None
    cur = None


    # ------------------
    # Internal functions
    # ------------------

    def __init__(self):
        # Initialize SQLite database
        self.con = sqlite3.connect("photo.db")
        self.cur = self.con.cursor()
        self.cur.executescript(DATABASE_STRUCTURE)
        self.scan()

        # Other functions
        register_heif_opener()

    def __str__(self):
        s = "The database:\n"
        # s += f" - contains {len(self.db['photos'].keys())} records\n"
        # s += f" - uses {int(sys.getsizeof(self.db['photos']) / 1024)} kilobytes of memory"
        return s


    # -------------------
    # Database population
    # -------------------

    def scan(self):
        root = Path(PHOTO_FOLDER)
        years = os.listdir(root)
        l = []
        for y in years:
            if PATTERN_YEAR.match(y):
                l.append(y)
        years = l
        years.sort(reverse=True)

        for y in years:
            for t in os.listdir(root / y):
                if t not in IGNORE:
                    files = os.listdir(root / y / t)
                    for f in files:
                        if f not in IGNORE:
                            if PATTERN_PHOTO.match(f):
                                photo_id = os.path.splitext(f)[0][4:].replace("_","")
                                photo_path = f"{y}/{t}/{f}"
                                print(f"Inserting {photo_id} (path {photo_path})")
                                self.cur.execute("INSERT OR REPLACE INTO Photos (ID, file_path) VALUES (?, ?)", (photo_id, photo_path))
                                self.con.commit()


    # ------------------------------
    # Metadata extraction/generation
    # ------------------------------

    def extract_exif(self, pid: str):
        return None # TODO rework with SQLite

        out = ""
        try:
            out = subprocess.run(['exiftool', '-j', Path(PHOTO_FOLDER) / self.db['photos'][pid]['path']], stdout=subprocess.PIPE).stdout.decode(encoding='utf-8')
            out = json.loads(out)[0]
        except Exception as e:
            print(f"Can't read metadata with exiftool: {str(e)}")
            return False

        # Timestamp
        if 'CreateDate' in out.keys():
            self.db['photos'][pid]['timestamp'] = out['CreateDate']
        else:
            # If no data, assume it's taken in Spain timezone (CEST, UTC+2)
            t = f"{pid[0:4]}-{pid[4:6]}-{pid[6:8]}T{pid[8:10]}:{pid[10:12]}:{pid[12:14]}+02:00"
            self.db['photos'][pid]['timestamp'] = t

        # Location
        try:
            self.db['photos'][pid]['altitude'] = out['GPSAltitude']
            self.db['photos'][pid]['latitude'] = out['GPSLatitude']
            self.db['photos'][pid]['longitude'] = out['GPSLongitude']
        except:
            print(f"Missing some or all coordinates on {pid}, can't extract location")

        # Update record modification time
        self.db['photos'][pid]['record']['last_modified'] = datetime.datetime.now().timestamp()

        return pid

    def resolve_location(self, pid):
        return None # TODO rework with SQLite
        return True

    def encode_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((1024, 1024))
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def describe(self, pid, llm):
        return None # TODO rework with SQLite
        print(f"Describing {pid}")
        base64_image = self.encode_image(PHOTO_FOLDER + "/" + self.db["photos"][pid]["path"])
        response = llm.responses.create(
            input = [{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": DESCRIPTION_PROMPT},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                ]
            }]
        )
        response = response.output_text
        print(response)
        # Some cleanup of common issues with smaller models
        response = response.replace("```json", "")
        response = response.replace("```", "")
        response = json.loads(str(response))
        self.db["photos"][pid]["description"] = response["description"]
        self.db["photos"][pid]["tags"] = response["tags"]
        return True

    def describe_all(self, overwrite=False):
        return None # TODO rework with SQLite
        llm = OpenAI(
            base_url = f"http://{LLAMAFILE_HOST}:{LLAMAFILE_PORT}/v1",
            api_key = "ollama"
            )
        for p in self.db['photos'].keys():
            self.describe(p, llm)
        return True



# =========================
#          SERVER
# =========================


p = PhotoDB()

app = Flask(__name__)

@app.route("/")
def root():
    return {"message": str(p)}

@app.route("/photos/all")
def get_all():
    return {"message": "Hello world!"}

@app.route("/search/<query>")
def search(query):
    return {"message": f"Query is {query}"}
