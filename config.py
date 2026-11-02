import re


PHOTO_FOLDER="./photo_folder"

PATTERN_YEAR = re.compile(
    '^(19[0-9]{2})|(20[0-9]{2})$'
    )
PATTERN_PHOTO = re.compile(
    '^IMG_[0-9]{8}_[0-9]{6}\\.(heic|jpg|jpeg|png|mov|mp4)$',
    flags=re.IGNORECASE)
IGNORE = [
        '.DS_Store'
    ]

DATABASE_FILE = "db.json"
LLAMAFILE_HOST = "127.0.0.1"
LLAMAFILE_PORT = "1290"
DESCRIPTION_PROMPT = "Output a JSON dictionary, with no extra formatting, \
    with two fields. The first is 'description' of the picture, between 50 \
    and 100 words, simple, clear and honest. The second is 'tags', a list \
    of 10 single word tags that describe the image, concisely and clearly."

DATABASE_STRUCTURE = """
CREATE TABLE IF NOT EXISTS Photos (
    ID INT PRIMARY KEY,
    file_path VARCHAR(256) NOT NULL,
    location VARCHAR(256),
    altitude REAL,
    latitude REAL,
    longitude REAL,
    time_stamp VARCHAR(64),
    description VARCHAR(2048),
    tags VARCHAR(1024),
    last_modified VARCHAR(64)
)
"""