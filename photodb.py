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
        with sqlite3.connect("photo.db") as con:
            cur = con.cursor()
            cur.executescript(DATABASE_STRUCTURE)

        # Other functions
        register_heif_opener()


    def __str__(self):
        s = ""
        with sqlite3.connect("photo.db") as con:
            cur = con.cursor()
            for row in cur.execute("SELECT * FROM dbstat"):
                s += str(row) + ", "
        if len(s) > 0:
            s = s[:-2]
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

        with sqlite3.connect("photo.db") as con:
            cur = con.cursor()
            for y in years:
                for t in os.listdir(root / y):
                    if t not in IGNORE:
                        files = os.listdir(root / y / t)
                        for f in files:
                            if f not in IGNORE:
                                if PATTERN_PHOTO.match(f):
                                    photo_id = os.path.splitext(f)[0][4:].replace("_","")
                                    photo_path = f"{y}/{t}/{f}"
                                    print(f"Found {photo_path}")
                                    try:
                                        cur.execute("INSERT OR IGNORE INTO Photos (ID, file_path) VALUES (?, ?)", (photo_id, photo_path))
                                    except Exception as e:
                                        print(f"Error executing or committing insertion: {e}")


    # --------------
    # Data retrieval
    # --------------

    def get_all(self):
        results = []
        with sqlite3.connect("photo.db") as con:
            cur = con.cursor()
            for row in cur.execute("SELECT ID, file_path FROM Photos"):
                results.append(row)
        return results


    # ------------------------------
    # Metadata extraction/generation
    # ------------------------------

    def extract_exif(self):

        with sqlite3.connect("photo.db") as con:
            cur = con.cursor()
            todo_list = []

            for row in cur.execute("SELECT ID, file_path FROM Photos WHERE time_stamp IS NULL ORDER BY ID"):
                todo_list.append(row)

            for row in todo_list:
                ID = row[0]
                file_path = row[1]
                print(f"Extracting metadata from {file_path}")
                try:
                    out = ""
                    try:
                        out = subprocess.run(['exiftool', '-j', Path(PHOTO_FOLDER) / file_path], stdout=subprocess.PIPE).stdout.decode(encoding='utf-8')
                        out = json.loads(out)[0]
                    except Exception as e:
                        print(f"Can't read metadata with exiftool: {str(e)}")
                        return False

                    # Timestamp
                    new_timestamp = None
                    if 'CreateDate' in out.keys():
                        new_timestamp = out['CreateDate']
                    elif 'FileModifyDate' in out.keys():
                        new_timestamp = out['FileModifyDate']
                    else:
                        # If no data, create it from the filename
                        id_str = str(ID)
                        new_timestamp = f"{id_str[0:4]}-{id_str[4:6]}-{id_str[6:8]}T{id_str[8:10]}:{id_str[10:12]}:{id_str[12:14]}"

                    # Location
                    new_latitude = out['GPSLatitude'] if 'GPSLatitude' in out.keys() else "N/A"
                    new_longitude = out['GPSLongitude'] if 'GPSLongitude' in out.keys() else "N/A"
                    new_altitude = out['GPSAltitude'] if 'GPSAltitude' in out.keys() else "N/A"

                    # Update record modification time
                    new_last_modified = datetime.datetime.now().timestamp()

                    # Insert all new data
                    cur.execute("""
                        UPDATE Photos SET
                        time_stamp = ?,
                        altitude = ?,
                        latitude = ?,
                        longitude = ?,
                        last_modified = ?
                        WHERE ID = ?
                        """, (new_timestamp, new_altitude, new_latitude, new_longitude, new_last_modified, ID))
                except Exception as e:
                    print(f"Error when extracting metadata of {ID}: {e}")
                    return False


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


# Scanning and deterministic information extraction

@app.route("/scan")
def scan():
    try:
        p.scan()
    except Exception as e:
        return {"message": "Scan error"}, 500
    return {"message": "Scan complete"}

@app.route("/extract_metadata")
def extract_metadata():
    try:
        p.extract_exif()
    except Exception as e:
        return {"message": "Metadata extraction error"}, 500
    return {"message": "Metadata extraction complete"}


# Picture querying

@app.route("/photos")
def get_all():
    reply = None
    try:
        reply = p.get_all()
        return {"message": "OK", "payload": reply}
    except Exception as e:
        return {"message": f"Couldn't get all photos: {e}"}

@app.route("/photos/<query>")
def photos(query):
    return {"message": f"Query is {query}"}
