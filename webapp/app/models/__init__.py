# coding: utf-8
import logging
import pathlib
import os
import datetime
import ast
import random
import numpy as np
import pandas
import plotly.express as px
import plotly.offline.offline as poff
from io import BytesIO
from matplotlib import pyplot
from matplotlib import dates as mdates
from operator import or_
from flask_sqlalchemy import SQLAlchemy
from flask import request, url_for, send_file, make_response
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_, func
from sqlalchemy.sql.operators import endswith_op



db = SQLAlchemy()
viz_dir = pathlib.PurePath("/viz")
logger = logging.getLogger("gunicorn.error")
max_plots = 5

class Plotter(object):

    @staticmethod
    def get_current_chart():
        path = viz_dir / "chart"
        if os.path.isfile(str(path / "current.html")):
            out = str(path / "current.html")
        else: 
            out = str(path / "blank-chart.html")
        with open(out, "r") as f:
            response = make_response(f.read())
            response.mimetype = "text/html"
            return response

    @staticmethod
    def chart_types():
        return [
            {"id": "scatter", "display": "Scatterplot"},
            {"id": "grad_scatter", "display": "Bubble Chart (only one measure)"},
            {"id": "bar", "display": "Bar Chart"},
            {"id": "histogram", "display": "Histogram"},
        ]

    @staticmethod
    def call(*args, **kwargs):
        verb = request.method.lower()
        if hasattr(Plotter, verb):
            return getattr(Plotter, verb)(*args, **kwargs)
        else:
            return {"message": "Method not allowed."}, 405


    @staticmethod
    def retrieve_data(**kwargs):
        kwargs = Plotter.transform_input(**kwargs)
        measure_objects = kwargs.get("measures")
        location_objects = kwargs.get("locations")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        frames = []
        for i, measure in enumerate(measure_objects):
            for j, location in enumerate(location_objects):
                query = db.session.query(
                    WaterwayReading.id,
                    Location.display.label("location"),
                    Location.longitude,
                    Location.latitude,
                    WaterwayReading.sample_date.label("sample_date"), 
                    WaterwayReading.value.label("value"),
                    Chemical.display + "(" + UnitOfMeasure.unit_name + ")",
                    UnitOfMeasure.unit_name.label("unit"),
                ).join(
                    Chemical, WaterwayReading.chemical_id == Chemical.id
                ).join(
                    Location, WaterwayReading.location_id == Location.id
                ).join(
                    UnitOfMeasure, Chemical.unit_of_measure_id == UnitOfMeasure.id
                ).filter(
                    WaterwayReading.sample_date.between(start_date, end_date)
                )
                if location:
                    query = query.filter(WaterwayReading.location == location)
                if measure:
                    query = query.filter(WaterwayReading.chemical == measure)
                frames.append(
                    pandas.read_sql(
                        query.statement.compile(compile_kwargs={"literal_binds": True}),
                        db.session.bind
                    )
                )                
        df = pandas.concat(frames)
        df.columns = ["id", "location", "longitude", "latitude", "sample_date", "value", "measure", "unit"]
        return {
            "dataframe": df, 
            "locations": location_objects,
            "measures": measure_objects
        }
                        
    @staticmethod
    def post(*args, **kwargs):
        chart_type = request.form.get("chart_type")
        if not chart_type:
            return {"message": "You must specify a chart type."}, 401
        else:
            return Plotter.plot(**dict(request.form))


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
            measure_obj_list = []
            for m in measures:
                measure_obj_list.append(
                    Chemical.query.filter(Chemical.id == m).first()   
                )
            if not measure_obj_list:
                out_args["measures"] = Chemical.query.all()
            else:    
                out_args["measures"] = measure_obj_list
                
        if "locations" not in exclude:
            locations = ast.literal_eval(kwargs.get("locations"))
            location_obj_list = []
            for l in locations:
                location_obj_list.append(
                    Location.query.filter(Location.id == l).first()   
                )
            
            if not location_obj_list or kwargs.get("chart_type") == "density_heatmap":
                out_args["locations"] = Location.query.all()
            else:
                out_args["locations"] = location_obj_list

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
    def plot(**kwargs):
        data = Plotter.retrieve_data(**kwargs)
        df = data["dataframe"]
        ct = kwargs["chart_type"]
        
        if not data.get("locations"):
            return {"message": "You must select at least one location."}, 400
        if not data.get("measures"):
            return {"message": "You must select at least one measure."}, 400
        
        condense = kwargs.get("condenser")
        in_kwargs = dict(
            x="sample_date", 
            y="value", 
            facet_col="location",
            facet_row="measure", 
            height=800,
            width=1000, 
        )
        
        if ct == "grad_scatter":
            in_kwargs["y"] = "location"
            in_kwargs["size"] = "value" 
            in_kwargs["size_max"] = 80
            in_kwargs["color"] = "location"
            in_kwargs.pop("facet_col", None)
            in_kwargs.pop("facet_row", None)
            
            if len(data["measures"]) > 1:
                return {"message": "You can only use one measure for this chart type."}, 400
             
        
        if ct == "histogram":
            in_kwargs.pop("y", None)
        
    
        num_measures = len(data["measures"])
        if condense and num_measures == 1:
            in_kwargs.pop("facet_col", None)
            in_kwargs.pop("facet_row", None)
            in_kwargs["color"] = "location"
        elif num_measures != 1 and condense:
            return {"message": "You can only specify one measure type for a condensed chart."}, 400
        
        func = px.scatter if ct == "grad_scatter" else getattr(px, ct)
        fig = func(
            df, 
            **in_kwargs
        )

        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        html = poff.plot(
            fig, 
            include_plotlyjs=False, 
            output_type="div"
        )
                
        response = make_response(html)
        response.mimetype = "text/html"
        return response, 201
       


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

    @hybrid_property
    def location_measure(self):
        return f"{self.location.display} - {self.chemical.display}"

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
