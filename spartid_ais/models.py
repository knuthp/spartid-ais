from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    SmallInteger,
    String,
    Boolean,
)

from spartid_ais import db
from pyais.constants import NavigationStatus, ManeuverIndicator


class LastPositionReport(db.Model):
    __tablename__ = "last_position"

    mmsi = Column(Integer, primary_key=True, unique=True, index=True)
    lat = Column(Float)
    long = Column(Float)
    speed = Column(Float)
    course = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime)


class HistoricPositionReport(db.Model):
    __tablename__ = "historic_position"
    id = Column(Integer, primary_key=True)
    msg_type = Column(SmallInteger)
    repeat = Column(SmallInteger)
    mmsi = Column(Integer, index=True)
    status = Column(Enum(NavigationStatus))
    turn = Column(Float)
    speed = Column(Float)
    accuracy = Column(Boolean)
    lat = Column(Float)
    long = Column(Float)
    course = Column(Float)
    heading = Column(Integer)
    maneuver = Column(Enum(ManeuverIndicator))
    raim = Column(Boolean)
    radio = Column(Integer)
    timestamp = Column(DateTime)


class ImoVesselCodes(db.Model):
    __tablename__ = "imo_vessel_codes"
    mmsi = Column(Integer, primary_key=True, unique=True, index=True)
    imo = Column(String)
    name = Column(String)
    flag = Column(String)
    type = Column(String)


def init_app(app):
    return db
