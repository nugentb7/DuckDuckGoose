#!/usr/bin/env python3
import logging
import os
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, session
from models import db, Location, Chemical, WaterwayReading, Plotter

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///waterways.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

gunicorn_logger = logging.getLogger("gunicorn.error")
socketio = SocketIO(app)
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

db.init_app(app)


@app.route("/")
def index():
    return render_template(
        "index.html",
        sensors=Location.all_sensors(),
        min_date=WaterwayReading.min_sample_date(),
        max_date=WaterwayReading.max_sample_date(),
        chart_types=Plotter.chart_types()
    )

@app.route("/rest/location/<int:id>", methods=["GET"])
@app.route("/rest/location/name/<string:id>")
@app.route("/rest/locations/", methods=["GET"])
def location(id=None):
    return Location.get(id)

@app.route("/chart", methods=["POST"])
@app.route("/chart/<chart_type>/latest", methods=["GET"])
def chart(chart_type=None):
    return Plotter.call(chart_type=chart_type)
    
@app.route("/rest/measure", methods=["GET"])
def measure():
    return Chemical.search()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
