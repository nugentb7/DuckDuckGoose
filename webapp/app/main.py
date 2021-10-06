#!/usr/bin/env python3
import logging
from flask import Flask, render_template
from models import db, Location, Chemical, WaterwayReading

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
    return render_template(
        "index.html",
        sensors=Location.all_sensors(),
        min_date=WaterwayReading.min_sample_date(),
        max_date=WaterwayReading.max_sample_date()
    )

@app.route("/rest/location/<int:id>", methods=["GET"])
@app.route("/rest/location/name/<string:id>")
@app.route("/rest/locations/", methods=["GET"])
def location(id=None):
    return Location.get(id)
    
@app.route("/rest/measure", methods=["GET"])
def measure():
    return Chemical.search()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
