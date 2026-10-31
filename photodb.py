from pillow_heif import register_heif_opener
from flask import Flask, jsonify
from openai import OpenAI
from pathlib import Path
from io import BytesIO
from PIL import Image
import subprocess
import datetime
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

    config = {}
    db = {}


    # ------------------
    # Internal functions
    # ------------------

    def __init__(self):
        self.db['photos'] = {}
        register_heif_opener()

    def __str__(self):
        s = "The database:\n"
        # s += f" - contains {len(self.db['photos'].keys())} records\n"
        # s += f" - uses {int(sys.getsizeof(self.db['photos']) / 1024)} kilobytes of memory"
        return s


    # ------------------------
    # Database file management
    # ------------------------

    def save(self):
        return None # TODO rework with SQLite
        try:
            with open(self.config['database_file'], mode='w') as db_file:
                return json.dump(self.db, db_file, sort_keys=True)
        except Exception as e:
            print(f"Couldn't write database to file: {str(e)}")
            return None

    def load(self):
        return None # TODO rework with SQLite
        try:
            with open(self.config['database_file'], mode='r') as db_file:
                self.db = json.load(db_file)
                return self.db
        except Exception as e:
            print(f"Couldn't read database from file: {str(e)}")
            return None


    # ------------------------
    # Database entry functions
    # ------------------------

    def photo_get(self, pid: str):
        return None # TODO rework with SQLite
        if self.db['photos'][pid]:
            return self.db['photos'][pid].copy()
        else:
            return None

    def photo_set(self, pid: str, path: str):
        return None # TODO rework with SQLite
        photo = {}
        photo['path'] = path
        photo['record'] = {}
        self.db['photos'][pid] = photo
        return pid


    # -------------------
    # Database population
    # -------------------

    def scan(self):
        return None # TODO rework with SQLite
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
                                self.photo_set(os.path.splitext(f)[0][4:].replace("_",""), f"{y}/{t}/{f}")


    # -------------------
    # Metadata extraction
    # -------------------

    def extract_exif(self, pid: str):
        return None # TODO rework with SQLite

        # -- PHOTO ENTRY PROTOTYPE --
        # "20240313165414": {
        #   "path": "2024/car pics/IMG_20240313_165414.png",
        #   "location": "Getafe, Madrid",
        #   "altitude": ""
        #   "latitude": ""
        #   "longitude": ""
        #   "timestamp": "2024-03-13T16:54:14+02:00"
        #   "description": "A picture of a silver convertible on an european street made of cobblestone",
        #   "tags": ["car", "small street", "morning", "chill"]
        #   "record": {
        #       "last_modified": "1776933993.213789"
        # }

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

    def extract_exif_all(self, overwrite=False):
        return None # TODO rework with SQLite
        for p in self.db['photos'].keys():
            self.extract_exif(p)
        return True


    # -------------------
    # Metadata generation
    # -------------------

    def resolve_location(self, pid):
        return None # TODO rework with SQLite
        return True

    def resolve_location_all(self, overwrite=False):
        return None # TODO rework with SQLite
        for p in self.db['photos'].keys():
            self.resolve_location(p)
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
                    {"type": "input_text", "text": self.config["description_prompt"]},
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
            base_url = f"http://{self.config["llamafile_host"]}:{self.config["llamafile_port"]}/v1",
            api_key = "ollama"
            )
        for p in self.db['photos'].keys():
            self.describe(p, llm)
        return True


    # ----------------
    # Other operations
    # ----------------

    def sanitize(self):
        return True



# =========================
#          SERVER
# =========================


p = PhotoDB()

app = Flask(__name__)

@app.route("/")
def root():
    return {"message": str(p)}

@app.route("/load")
def load():
    p.load()
    return {"message": str(p)}

@app.route("/photos/all")
def get_all():
    return jsonify(p.db)

@app.route("/search/<query>")
def search(query):
    if (query == "all"):
        return jsonify(p.db)
    else:
        return jsonify(p.db)
