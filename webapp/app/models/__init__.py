# coding: utf-8
import logging
import pathlib
import os
import datetime
import ast
import random
import numpy as np
from io import BytesIO
from matplotlib import pyplot
from matplotlib import dates as mdates
from operator import or_
from flask_sqlalchemy import SQLAlchemy
from flask import request, url_for, send_file
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_, func
from sqlalchemy.sql.operators import endswith_op
import plotly.express as px



db = SQLAlchemy()
viz_dir = pathlib.PurePath("/viz")
logger = logging.getLogger("gunicorn.error")
max_plots = 5

class Plotter(object):

    @staticmethod
    def chart_types():
        return [
            {"id": "scatterplot", "display": "Scatterplot"},
            {"id": "line_chart", "display": "Line Chart"}
        ]

    @staticmethod
    def call(*args, **kwargs):
        verb = request.method.lower()
        if hasattr(Plotter, verb):
            return getattr(Plotter, verb)(*args, **kwargs)
        else:
            return {"message": "Method not allowed."}, 405

    @staticmethod
    def get(chart_type=None):
        if request.path.endswith("latest"):
            path = str(viz_dir / chart_type)
            files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            logger.info(files)
            if files:
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                newest = files[0]
                with open(newest, "rb") as f_bytes:
                    return send_file(
                        BytesIO(f_bytes.read()),
                        mimetype="image/png",
                        as_attachment=True,
                        attachment_filename=f"{chart_type}.png"
                    )
            else: 
                return {"message": "Not found."}, 404
        else:
            return {"message": "Not supported."}, 400


    @staticmethod
    def post(*args, **kwargs):
        chart_type = request.form.get("chart_type")
        if not chart_type:
            return {"message": "You must specify a chart type."}, 401
        else:
            if hasattr(Plotter, chart_type):                
                return getattr(Plotter, chart_type)(**dict(request.form))
            else: 
                return {"message": "Not found."}, 401


    @staticmethod
    def line_chart(**kwargs):
        kwargs = Plotter.transform_input(**kwargs)
        measure_objects = kwargs.get("measures")
        location_objects = kwargs.get("locations")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        if not measure_objects:
            return {"message": "Invalid measure inputs."}, 401
        if not location_objects:
            return {"message": "Invalid location inputs."}, 401
        if len(set([m.unit_of_measure.id for m in measure_objects])) > 1:
            return {"message": "You must choose measures with the same unit of measurement."}, 401
        colors = ["blue", "green", "orange", "red"]
        i = 0
        title_string = []
        location_strings = set()
        pyplot.rc('font', size=12)
        fig, ax = pyplot.subplots(figsize=(10, 6))
        for measure in measure_objects:        
            title_string.append(measure.display)
            for location in location_objects:

                query = db.session.query(
                    db.distinct(db.func.date(WaterwayReading.sample_date).label("sample_date")), 
                    db.func.avg(WaterwayReading.value).label("value")
                ).join(
                    Chemical, Chemical.id == WaterwayReading.chemical_id
                ).join(
                    Location, Location.id == WaterwayReading.location_id
                ).group_by(
                    Location.id, 
                    Chemical.id, 
                    db.func.date(WaterwayReading.sample_date)
                ).filter(
                    Chemical.id == measure.id, 
                    Location.id == location.id, 
                )

                # query = db.session.query(
                #     WaterwayReading.sample_date, 
                #     WaterwayReading.value
                # ).filter(
                #     WaterwayReading.chemical == measure,
                #     WaterwayReading.location == location, 
                #     WaterwayReading.sample_date.between(start_date, end_date)
                # )

                location_strings.add(location.display)
                results = query.all()
                if results:
                    sample_dates, values = zip(*results)
                    ax.plot_date(sample_dates, values, fmt='H')
                    # ax.setp(plt.gca().xaxis.get_majorticklabels(),
                    #         'rotation', 90)
                    # ax.plot(sample_dates, values, color=f"tab:{colors[i]}", label=f"{location.display} - {measure.display}")

                    i += 1
        title_string = " and ".join(title_string) + " Over Time\n" + ", ".join(location_strings)
        ax.set_xlabel("Sample Dates")
        
        
        sample_measurment = measure_objects[0]
        ax.set_ylabel(f"Value ({sample_measurment.unit_of_measure})")
        ax.set_title(title_string)
        ax.grid(True)
        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])
        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, prop={'size': 9})
        Plotter.save_plot("line_chart")
        return {"message": "Successfully created.", "uri": f"/chart/line_chart/latest?t={random.randint(1, 99999999)}"}, 201


    @staticmethod
    def save_plot(directory):
        path = str(viz_dir / directory)
        files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        files.sort(key=lambda x: os.path.getmtime(x))
        if len(files) == max_plots:
            os.remove(files[0])
        pyplot.savefig(os.path.join(path, f"plot-{datetime.datetime.now().strftime('%Y%m%d%h%M')}.png"))


    @staticmethod
    def transform_input(**kwargs):
        input_args = kwargs

        exclude = kwargs.pop("exclude", [])
        if exclude:
            for arg in exclude:
                input_args.pop(arg, None)
        out_args = {}

        if "measures" not in exclude:
            measures = ast.literal_eval(kwargs.get("measures"))
            out_args["measures"] = Chemical.query.filter(Chemical.id.in_(measures)).all()
        if "locations" not in exclude:
            locations = ast.literal_eval(kwargs.get("locations"))
            out_args["locations"] = Location.query.filter(Location.id.in_(locations)).all()

        if "start_date" not in exclude:
            start_date = kwargs.get("start_date")
            if not start_date:
                start_date = datetime.datetime(1998, 1, 1)
            else:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            out_args["start_date"] = start_date
        if "end_date" not in exclude:
            end_date = kwargs.get("end_date")
            if not end_date:
                end_date = datetime.datetime.now()
            else:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            out_args["end_date"] = end_date
        return out_args


    @staticmethod
    def scatterplot(**kwargs):
        kwargs = Plotter.transform_input(**kwargs)
        measure_objects = kwargs.get("measures")
        location_objects = kwargs.get("locations")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        if not measure_objects:
            return {"message": "Invalid measure inputs."}, 401

        if not location_objects:
            return {"message": "Invalid location inputs."}, 401

        if len(set([m.unit_of_measure.id for m in measure_objects])) > 1:
            return {"message": "You must choose measures with the same unit of measurement."}, 401


        colors = ["blue", "green", "orange", "red"]
        i = 0
        title_string = []
        location_strings = set()
        pyplot.rc('font', size=12)
        fig, ax = pyplot.subplots(figsize=(10, 6))
        for measure in measure_objects:        
            title_string.append(measure.display)
            for location in location_objects:
                query = db.session.query(
                    WaterwayReading.sample_date, 
                    WaterwayReading.value
                ).filter(
                    WaterwayReading.chemical == measure,
                    WaterwayReading.location == location, 
                    WaterwayReading.sample_date.between(start_date, end_date)
                )

                location_strings.add(location.display)
                results = query.all()
                if results:
                    sample_dates, values = zip(*results)
                    ax.scatter(sample_dates, values, color=f"tab:{colors[i]}", label=f"{location.display} - {measure.display}", s=1)
                    i += 1

        title_string = " and ".join(title_string) + " Over Time\n" + ", ".join(location_strings)
        ax.set_xlabel("Sample Dates")
        
        sample_measurment = measure_objects[0]
        ax.set_ylabel(f"Value ({sample_measurment.unit_of_measure})")
        ax.set_title(title_string)
        ax.grid(True)

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, prop={'size': 9})
        Plotter.save_plot("scatterplot")
        return {"message": "Successfully created.", "uri": f"/chart/scatterplot/latest?t={random.randint(1, 99999999)}"}, 201
       


class Chemical(db.Model):
    __tablename__ = 'chemical'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display = db.Column(db.String(100), nullable=False)
    unit_of_measure_id = db.Column(db.ForeignKey('unit_of_measure.id'))

    unit_of_measure = db.relationship('UnitOfMeasure', primaryjoin='Chemical.unit_of_measure_id == UnitOfMeasure.id', backref='chemicals')

    @property
    def json(self):
        return {
            "id": int(self.id),
            "name": self.name, 
            "display": self.display,
            "unit": str(self.unit_of_measure.unit_name.decode()), 
            "uri": f"/rest/measure/{self.id}"
        }

    @staticmethod
    def get(id):
        if not id:
            return {"message": "Not found"}, 404
        else:
            result = Chemical.query.filter_by(id=id).first()
            if result:
                return result.json, 200
            else:
                return {"message": "Measure not found."}, 404


    @staticmethod
    def search():
        term = request.args.get("term")
        if not term:
            return {"results": []}, 200
        else:
            term = str(term).upper()
            results = Chemical.query.filter(
                or_(
                    Chemical.name.like(f"{term}%"), 
                    func.upper(Chemical.display).like(f"{term}%")
                )
            ).order_by(Chemical.name).all()
            return {"results": [{"id": r.id, "text": f"{r.display} ({str(r.unit_of_measure)})"} for r in results]}, 200



class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Numeric, nullable=False)
    latitude = db.Column(db.Numeric, nullable=False)
    location_type_id = db.Column(db.ForeignKey('location_type.id'))

    location_type = db.relationship('LocationType', primaryjoin='Location.location_type_id == LocationType.id', backref='locations')


    @staticmethod
    def all_sensors():
        return Location.query.filter_by(
            location_type=LocationType.query.filter_by(name="SENSOR").first()
        ).order_by(Location.name).all()


    @staticmethod
    def get(id=None):
        if id:
            if isinstance(id, str):
                results = Location.query.filter_by(name=id.upper()).first()
            else:
                results = Location.query.filter_by(id=id).first()
            if results:
                response = results.geojson, 200
            else:
                response = { "message" : "Not found." }, 404
        else:
            response = Location.all_locations_geojson(include_waste=not(request.args.get("nowaste") == "Y")), 200
        return response

    @hybrid_property
    def lat_long(self):
        return [float(self.latitude), float(self.longitude)]

    @hybrid_property
    def long_lat(self):
        return [float(self.longitude), float(self.latitude)]

    @hybrid_property
    def geojson(self):
        return { 
            "type": "Feature", 
            "properties": { 
                "id": self.id, 
                "name": self.name, 
                "display": self.display,
                "type": {
                    "id": self.location_type.id,
                    "name": self.location_type.name, 
                    "description": self.location_type.description
                }, 
                "uri": f"/rest/location/{int(self.id)}" 
            }, 
            "geometry": { 
                "type": "Point", 
                "coordinates": self.long_lat
            }, 
            "icon": {
                "iconUrl": url_for("static", filename=("icons/" + ("waste.png" if self.location_type.name == "WASTE" else "sensor.png"))),
                "iconSize": [30, 30], 
                "latlng": self.lat_long
            },
            "style": {
                "color": "red" if self.location_type.name == "SENSOR" else "green"
            } 
        }
    
    @property
    def json(self):
        return self.geojson

    @staticmethod
    def all_locations_geojson(include_waste=True):
        if include_waste:
            features = [location.geojson for location in Location.query.all()]
        else:
            features = [
                location.geojson for location in Location.query.filter_by(
                    location_type=LocationType.query.filter_by(name="SENSOR").first()
                ).all()
            ]
        return {
            "type": "FeatureCollection",
            "name": "sensor-locations",
            "crs": { 
                "type": "name", 
                "properties": { 
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84" 
                } 
            },
            "features": features
        }
    


class LocationType(db.Model):
    __tablename__ = 'location_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100))



class UnitOfMeasure(db.Model):
    __tablename__ = 'unit_of_measure'

    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String(10), unique=True)

    @property
    def decoded(self):
        return str(self.unit_name.decode())

    def __str__(self):
        return self.unit_name.decode()

    def __repr__(self):
        return str(self)


class WaterwayReading(db.Model):
    __tablename__ = 'waterway_reading'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric, nullable=False)
    chemical_id = db.Column(db.ForeignKey('chemical.id'), nullable=False)
    location_id = db.Column(db.ForeignKey('location.id'), nullable=False)
    sample_date = db.Column(db.Date, nullable=False)

    chemical = db.relationship('Chemical', primaryjoin='WaterwayReading.chemical_id == Chemical.id', backref='waterway_readings')
    location = db.relationship('Location', primaryjoin='WaterwayReading.location_id == Location.id', backref='waterway_readings')


    @property 
    def json(self):
        return {
            "id": int(self.id), 
            "value": float(self.value),
            "sample_date": self.sample_date.strftime("%Y-%m-%d"),
            "location": self.location.json, 
            "measure": self.chemical.json
        }


    @staticmethod
    def min_sample_date():
        return db.session.query(
            db.func.min(WaterwayReading.sample_date)
        ).scalar()

    @staticmethod
    def max_sample_date():
        return db.session.query(
            db.func.max(WaterwayReading.sample_date)
        ).scalar()

    @staticmethod
    def search():
        args = dict(request.args)
        args = WaterwayReading.transform_input(**args)
        
        location_ids = [loc.id for loc in args["locations"]]
        measure_ids = [ms.id for ms in args["measures"]]
        query = WaterwayReading.query.filter(
            db.between(
                WaterwayReading.sample_date,
                args["start_date"],
                args["end_date"]
            )
        )

        if location_ids:
            query = query.filter(WaterwayReading.location_id.in_(location_ids))
        if measure_ids:
            query = query.filter(WaterwayReading.chemical_id.in_(measure_ids))

        data = query.all()

        if data:
            response = {"results": [row.json for row in data], "message": "Ok."}, 200
        else:
            response = {"results": [], "message": "None found."}, 200
        return response


    @staticmethod
    def transform_input(**kwargs):
        input_args = kwargs

        exclude = kwargs.pop("exclude", [])
        if exclude:
            for arg in exclude:
                input_args.pop(arg, None)
        out_args = {}

        if "measures" not in exclude and kwargs.get("measures"):
            measures = ast.literal_eval(kwargs.get("measures"))
            out_args["measures"] = Chemical.query.filter(Chemical.id.in_(measures)).all()
        else: 
            out_args["measures"] = []

        if "locations" not in exclude and kwargs.get("locations"):
            locations = ast.literal_eval(kwargs.get("locations"))
            out_args["locations"] = Location.query.filter(Location.id.in_(locations)).all()
        else: 
            out_args["locations"] = []

        if "start_date" not in exclude:
            start_date = kwargs.get("start_date")
            if not start_date:
                start_date = datetime.datetime(1998, 1, 1)
            else:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            out_args["start_date"] = start_date
        if "end_date" not in exclude:
            end_date = kwargs.get("end_date")
            if not end_date:
                end_date = datetime.datetime.now()
            else:
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            out_args["end_date"] = end_date
        return out_args



class WaterwayReadingMaster(db.Model):
    __tablename__ = 'waterway_reading_master'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric)
    unit_name = db.Column(db.String)
    chemical = db.Column(db.String(100))
    location = db.Column(db.String(100))
    sample_date = db.Column(db.Date)
