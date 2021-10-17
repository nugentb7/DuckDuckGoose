#!/usr/bin/env python3
import pathlib
import argparse
import datetime
from matplotlib import pyplot
from sqlalchemy import create_engine, between
from sqlalchemy.orm import sessionmaker
from models import Chemical, Location, WaterwayReading, WaterwayReadingMaster


_parent_dir = pathlib.Path(__file__).resolve().parent
_default_db = _parent_dir / "waterways.db"


def with_args(f):
    def with_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Database schema initializer.")
        ap.add_argument("-p", "--database-path", type=str, help="Path to the sqlite3 database.", default=str(_default_db))
        ap.add_argument("-l", "--locations", type=int, nargs="+", help="Location IDs")
        ap.add_argument("-m", "--measures", type=int, nargs="+", help="Measure IDs")
        return f(ap.parse_args(), *args, **kwargs)
    return with_args_


def time_series(session, locations, measures, start_date=datetime.datetime(1998, 1, 1), end_date=datetime.datetime.now()):
    measure_objects = session.query(Chemical).filter(Chemical.id.in_(measures[:2])).all()
    location_objects = session.query(Location).filter(Location.id.in_(locations[:2])).all()

    colors = ["blue", "green", "orange", "red"]
    i = 0
    title_string = []
    location_strings = set()
    pyplot.rc('font', size=12)
    fig, ax = pyplot.subplots(figsize=(10, 6))
    for measure in measure_objects:        
        title_string.append(measure.display)
        for location in location_objects:
            query = session.query(
                WaterwayReading.sample_date, 
                WaterwayReading.value
            ).filter(
                WaterwayReading.chemical == measure,
                WaterwayReading.location == location, 
                WaterwayReading.sample_date.between(start_date, end_date)
            )

            location_strings.add(location.display)
            sample_dates, values = zip(*query.all())
            ax.scatter(sample_dates, values, color=f"tab:{colors[i]}", label=f"{location.display} - {measure.display}", s=1)
            i += 1

    title_string = " and ".join(title_string) + " Over Time\n" + ", ".join(location_strings)
    ax.set_xlabel("Sample Dates")
    ax.set_ylabel("Value")
    ax.set_title(title_string)
    ax.grid(True)

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, prop={'size': 9})

    pyplot.show()
    pyplot.savefig("plot.png")

    # ax.plot(sample_dates, , color='tab:orange', label='Windspeed')


@with_args
def main(cmd_line):
    engine = create_engine(f"sqlite:///{cmd_line.database_path}")
    session = sessionmaker(bind=engine)()

    time_series(session, cmd_line.locations, cmd_line.measures)

    session.commit()
    session.close()

if __name__ == "__main__":
    main()