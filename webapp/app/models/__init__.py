# coding: utf-8
import logging
from operator import or_
from flask_sqlalchemy import SQLAlchemy
from flask import request, url_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import or_, func


db = SQLAlchemy()


logger = logging.getLogger("gunicorn.error")


class Chemical(db.Model):
    __tablename__ = 'chemical'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display = db.Column(db.String(100), nullable=False)
    unit_of_measure_id = db.Column(db.ForeignKey('unit_of_measure.id'))

    unit_of_measure = db.relationship('UnitOfMeasure', primaryjoin='Chemical.unit_of_measure_id == UnitOfMeasure.id', backref='chemicals')


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
                    "name": self.location_type.name
                } 
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

    def __str__(self):
        return self.unit_name.decode()


class WaterwayReading(db.Model):
    __tablename__ = 'waterway_reading'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric, nullable=False)
    chemical_id = db.Column(db.ForeignKey('chemical.id'), nullable=False)
    location_id = db.Column(db.ForeignKey('location.id'), nullable=False)
    sample_date = db.Column(db.Date, nullable=False)

    chemical = db.relationship('Chemical', primaryjoin='WaterwayReading.chemical_id == Chemical.id', backref='waterway_readings')
    location = db.relationship('Location', primaryjoin='WaterwayReading.location_id == Location.id', backref='waterway_readings')


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


class WaterwayReadingMaster(db.Model):
    __tablename__ = 'waterway_reading_master'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric)
    unit_name = db.Column(db.String)
    chemical = db.Column(db.String(100))
    location = db.Column(db.String(100))
    sample_date = db.Column(db.Date)
