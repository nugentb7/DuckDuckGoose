#!/usr/bin/env python3
import argparse
import pathlib
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.engine import base
from models import Base

_parent = pathlib.Path(__file__).resolve().parent
_default_db = _parent / "waterways.db"


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
        for view in (_parent / "views").iterdir():
            try:
                engine.execute(
                    f"drop view {view.stem.replace('-', '_')}"
                )
            except sqlalchemy.exc.OperationalError:
                pass
    else:
        Base.metadata.create_all(bind=engine)
        base_view = _parent / "views" / "waterway-reading-master.sql"
        engine.execute(base_view.read_text())
        for view in (_parent / "views").iterdir():
            if view.name != base_view.name:
                engine.execute(
                    view.read_text()
                )


if __name__ == "__main__":
    main()
