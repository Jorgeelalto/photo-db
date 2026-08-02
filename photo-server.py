from flask import Flask, jsonify
from photodb import photodb


p = photodb.PhotoDB('config.yml')


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

@app.route("/search")
def search():
    return jsonify(p.db)