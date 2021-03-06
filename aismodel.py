from sqlalchemy import Column, Integer, Float, DateTime, String
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ShipDetails(db.Model):
    __tablename__= 'ShipDetails'
    
    mmsi = Column(Integer, primary_key=True, unique=True, index=True)    
    name = Column(String)


class LastPositionReport(db.Model):
    __tablename__ = 'LastPosition'
    
    mmsi = Column(Integer, primary_key=True, unique=True, index=True)    
    lat = Column(Float)
    long = Column(Float)
    speed = Column(Float)
    course = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime)
    
class HistoricPositionReport(db.Model):
    __tablename__ = 'HistoricPosition'
    id = Column(Integer, primary_key=True)
    mmsi = Column(Integer, index=True)    
    lat = Column(Float)
    long = Column(Float)
    timestamp = Column(DateTime)


class ImoVesselCodes(db.Model):
    __tablename__ = 'ImoVesselCodes'
    mmsi = Column(String, primary_key=True, unique=True, index=True)    
    imo  = Column(String)
    name = Column(String)
    flag = Column(String)        
    type = Column(String)