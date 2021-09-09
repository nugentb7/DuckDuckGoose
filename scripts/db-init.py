#!/usr/bin/env python3
import argparse
import pathlib
from sqlalchemy import create_engine
from models import Base

_default_db = pathlib.Path(__file__).resolve().parent / "waterways.db"


def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Database schema initializer.")
        ap.add_argument("-p", "--database-path", type=str, help="Path to the sqlite3 database.", default=str(_default_db))
        ap.add_argument("-d", "--delete", action="store_true", help="If specified, will clear out the database.", default=False)
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


@with_args
def main(cmd_line):
    engine = create_engine(f"sqlite:///{cmd_line.database_path}")
    if cmd_line.delete:
        Base.metadata.drop_all(bind=engine)
        engine.execute("drop view waterway_reading_master")
    else:
        Base.metadata.create_all(bind=engine)
        engine.execute("""
            create view waterway_reading_master as 
            select ww.id
                 , ww.value 
                 , um.unit_name
                 , cm.display as chemical
                 , l.display as location
                 , ww.sample_date
            from waterway_reading ww 
            left join location l on ww.location_id = l.id
            left join chemical cm on ww.chemical_id = cm.id
            left join unit_of_measure um on cm.unit_of_measure_id = um.id
        """)


if __name__ == "__main__":
    main()
