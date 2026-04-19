from PIL import Image, ExifTags
from pathlib import Path
import subprocess
import json
import yaml
import sys
import os
import re


PATTERN_YEAR = re.compile(
	'^(19[0-9]{2})|(20[0-9]{2})$'
	)
PATTERN_PHOTO = re.compile(
	'^IMG_[0-9]{8}_[0-9]{6}\\.(heic|jpg|jpeg|png|mov|mp4)$',
	flags=re.IGNORECASE)
IGNORE = [
		".DS_Store"
	]



class PhotoDB:

	config = {}
	db = {}

	def __init__(self, config_path: str):
		try:
			with open(config_path) as config_file:
				self.config = yaml.safe_load(config_file)
		except Exception as e:
			print(f"Couldn't load config file: {str(e)}")
			return None
		self.db['photos'] = {}

	def __str__(self):
		s = "The database:\n"
		s += f" - contains {len(self.db['photos'].keys())} records\n"
		s += f" - uses {int(sys.getsizeof(self.db['photos']) / 1024)} kilobytes of memory"
		return s


	def save(self):
		try:
			with open(self.config['database_file'], mode='w') as db_file:
				return json.dump(self.db, db_file, sort_keys=True)
		except Exception as e:
			print(f"Couldn't write database to file: {str(e)}")
			return None

	def load(self):
		try:
			with open(self.config['database_file'], mode='r') as db_file:
				self.db = json.load(db_file)
				return self.db
		except Exception as e:
			print(f"Couldn't read database from file: {str(e)}")
			return None



	def photo_get(self, pid: str):
		if self.db['photos'][pid]:
			return self.db['photos'][pid].copy()
		else:
			return None

	def photo_set(self, pid: str, path: str):
		photo = {}
		photo['path'] = path
		self.db['photos'][pid] = photo
		return pid



	def scan(self):
		root = Path(self.config['photo_folder'])
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


	def analyze(self, pid: str):

		# -- PHOTO ENTRY PROTOTYPE --
		# "20240313165414": {
		#	"path": "2024/car pics/IMG_20240313_165414.png",
		#	"location": "Getafe, Madrid",
		#	"timestamp": "2024-03-13T16:54:14+02:00"
		#	"description": "A picture of a silver convertible on an european street made of cobblestone",
		#	"tags": ["car", "small street", "morning", "chill"]
		# }

		img = None
		try:
			img = Image.open(Path(self.config['photo_folder']) / self.db['photos'][pid]['path'])
		except Exception as e:
			print(f"Couldn't load image to be analyzed: {str(e)}")
			return False
		exif = img.getexif()
		if exif:
			for key, val in exif.items():
				if key in ExifTags.TAGS:
					print(f'{ExifTags.TAGS[key]}:{val}')
				else:
					print(f'{key}:{val}')
		return False

	def analyze_all(self):
		for p in self.db['photos'].keys():
			self.analyze(p)
		return True


	def sanitize(self):
		return False


p = PhotoDB('config.yml')
p.scan()
#p.save()
#p.analyze_all()
print(p)
