from flask import Flask, jsonify
from photodb import photodb


p = photodb.PhotoDB('config.yml')


app = Flask(__name__)


@app.route("/load")
def load():
    p.load()
    return str(p)

@app.route("/save")
def save():
    p.save()
    return str(p)

@app.route("/scan")
def scan():
    p.scan()
    return str(p)

@app.route("/analyze")
def analyze():
    p.extract_exif_all()
    #p.resolve_location_all()
    #p.describe_all()
    return str(p)

@app.route("/photos/all")
def get_all():
    return jsonify(p.db)
