from sqlalchemy import Column, DateTime, Float, Integer, String

from spartid_ais import db


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
    mmsi = Column(Integer, index=True)
    lat = Column(Float)
    long = Column(Float)
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
