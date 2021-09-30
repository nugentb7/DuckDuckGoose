#!/usr/bin/env python3
import logging
from flask import Flask
from models import db, Location

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///waterways.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>hello, world</h1>"

@app.route("/rest/location/<int:id>", methods=["GET"])
@app.route("/rest/location/name/<string:id>")
@app.route("/rest/locations/", methods=["GET"])
def location(id=None):
    return Location.get(id)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
