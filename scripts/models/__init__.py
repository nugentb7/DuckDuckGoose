from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.expression import null

Base = declarative_base()


class WaterwayReadingMaster(Base):
    __tablename__ = 'waterway_reading_master'
    __abstract__ = True

    id = Column(Integer)
    value = Column(Numeric)
    unit_name = Column(String(10))
    chemical = Column(String(100))
    location = Column(String(100))
    sample_date = Column(Date)


class UnitOfMeasure(Base):
    __tablename__ = "unit_of_measure"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique, serial ID.")
    unit_name = Column(String(10), nullable=True, comment="The unit of measure's name.", unique=True)


class Chemical(Base):
    __tablename__ = "chemical"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique, serial ID.")
    name = Column(String(100), nullable=False, comment="The chemical's name.", unique=True)
    display = Column(String(100), nullable=False, comment="The display string for this chemical.")
    unit_of_measure_id = Column(Integer, ForeignKey("unit_of_measure.id"), comment="Foreign key referense to the unit of measure.")

    unit_of_measure = relationship("UnitOfMeasure", backref="chemicals")


class LocationType(Base):
    __tablename__ = "location_type"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique, serial ID.")
    name = Column(String(100), unique=True, comment="Location type name.")
    description = Column(String(100), comment="Description of the location type.")



class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Unique, serial ID.")
    name = Column(String(100), nullable=False, comment="The name of the location.", unique=True)
    display = Column(String(100), nullable=False, comment="The display string for this location.")
    longitude = Column(Numeric, nullable=False, comment="Longitude (x) coordinate.")
    latitude = Column(Numeric, nullable=False, comment="Latitude (y) coordinate.")
    location_type_id = Column(Integer, ForeignKey("location_type.id"), comment="Foreign key referense to the location type.")

    location_type = relationship("LocationType", backref="locations")



class WaterwayReading(Base):
    __tablename__ = "waterway_reading"

    id = Column(Integer, primary_key=True, nullable=False, comment="Unique ID, provided in dataset.")
    value = Column(Numeric, nullable=False, comment="The numeric value of the reading.")
    chemical_id = Column(Integer, ForeignKey("chemical.id"), nullable=False, comment="Foreign key reference to the chemical that was read.")
    location_id = Column(Integer, ForeignKey("location.id"), nullable=False, comment="Foreign key reference to the location of this reading.")
    sample_date = Column(Date, nullable=False, comment="When this sample was taken.")

    chemical = relationship("Chemical", backref="waterway_readings")
    location = relationship("Location", backref="waterway_readings")
