from datetime import datetime
from sqlalchemy import (
    SmallInteger,
)

from sqlalchemy.orm import Mapped, mapped_column

from spartid_ais import db
from pyais.constants import NavigationStatus, ManeuverIndicator


class LastPositionReport(db.Model):
    __tablename__ = "last_position"

    mmsi: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    lat: Mapped[float]
    long: Mapped[float]
    speed: Mapped[float]
    course: Mapped[float]
    heading: Mapped[float]
    timestamp: Mapped[datetime]


class HistoricPositionReport(db.Model):
    __tablename__ = "historic_position"
    id: Mapped[int] = mapped_column(primary_key=True)
    msg_type: Mapped[int] = mapped_column(SmallInteger)
    repeat: Mapped[int] = mapped_column(SmallInteger)
    mmsi: Mapped[int] = mapped_column(index=True)
    status: Mapped[NavigationStatus]
    turn: Mapped[float]
    speed: Mapped[float]
    accuracy: Mapped[bool]
    lat: Mapped[float]
    long: Mapped[float]
    course: Mapped[float]
    heading: Mapped[int]
    maneuver: Mapped[ManeuverIndicator]
    raim: Mapped[bool]
    radio: Mapped[int]
    timestamp: Mapped[datetime]


class ImoVesselCodes(db.Model):
    __tablename__ = "imo_vessel_codes"
    mmsi: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    imo: Mapped[str]
    name: Mapped[str]
    flag: Mapped[str]
    type: Mapped[str]


def init_app(app):
    return db
