#!/usr/bin/env python3
import argparse
import pathlib
import csv
import logging
import chardet
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import UnitOfMeasure, Chemical, Location, WaterwayReading

logging.basicConfig(level=logging.DEBUG)

_parent_dir = pathlib.Path(__file__).resolve().parent
_default_db = _parent_dir / "waterways.db"
_csv_dir = _parent_dir / "raw-data"

def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Database schema initializer.")
        ap.add_argument("-p", "--database-path", type=str, help="Path to the sqlite3 database.", default=str(_default_db))
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


def units_and_chemicals(session):

    with open(_csv_dir / "units-of-measure.csv", "rb") as f:
        encoding = chardet.detect(f.read())["encoding"]

    with open(_csv_dir / "units-of-measure.csv", "r", encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=["measure", "unit"])
        next(reader)  # skip the header
        for row in reader:
            display = row["measure"].strip()
            name = row["measure"].upper()
            unit = row["unit"].strip()
            unit = (unit if unit else "N/A").encode("utf-8")

            logging.info(unit)
            # first check that a unit of measurement record exists
            unit_of_measure = session.query(UnitOfMeasure).filter_by(unit_name=unit).first()
            if not unit_of_measure:
                unit_of_measure = UnitOfMeasure(
                    unit_name=unit
                )
                session.add(unit_of_measure)
                session.flush()
                logging.info(f"{unit} unit of measure added.")
            
            # add the chemical, if not already there
            chemical = session.query(Chemical).filter_by(name=name).first()
            if not chemical:
                chemical = Chemical(
                    name=name, 
                    display=display,
                    unit_of_measure=unit_of_measure
                )
                session.add(chemical)
                session.flush()
                logging.info(f"{name} chemical added.")

    # add N/A chemical for blank vals
    session.add(
        Chemical(
            name="N/A",
            display="N/A",
            unit_of_measure=session.query(UnitOfMeasure).filter_by(unit_name="N/A").first()
        )
    )
    session.flush()


def locations_and_readings(session):
    with open(_csv_dir / "waterway-readings.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=["id", "value", "location", "date", "measure"])
        next(reader)  # skip the header

        for row in reader:
            location_display = row["location"].strip()
            location_name = location_display.upper()

            # create location, if needed
            location = session.query(Location).filter_by(name=location_name).first()
            if not location:
                location = Location(
                    name=location_name, 
                    display=location_display
                )
                session.add(location)
                session.flush()
            
            # get the correct chemical
            chemical_name = row["measure"].strip().upper()
            chemical = session.query(Chemical).filter_by(name=chemical_name).first()
            if not chemical:
                chemical = session.query(Chemical).filter_by(name="N/A").first()

            # add reading
            
            # handle special case for pre-2000 dates. we only get two digits, but string
            # formatters would possibly read 13 (2013) as 1913.
            sample_date = row["date"]
            parts = sample_date.split("-")
            year = parts[2]
            if year in ("98", "99"):  # ex) 98 (1998), 99 (1999)
                year = f"19{year}"
            else:
                year = f"20{year}"
            date = datetime.datetime.strptime(f"{parts[0]}-{parts[1]}-{year}", "%d-%b-%Y").date()
            
            reading = WaterwayReading(
                value=row["value"], 
                location=location, 
                chemical=chemical, 
                sample_date=date
            )
            session.add(reading)
            session.flush()


@with_args
def main(cmd_line):
    engine = create_engine(f"sqlite:///{cmd_line.database_path}")
    session = sessionmaker(bind=engine)()

    units_and_chemicals(session)
    locations_and_readings(session)

    session.commit()
    session.close()


if __name__ == "__main__":
    main()
