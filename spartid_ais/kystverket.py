import logging
from datetime import datetime, timedelta
import sqlite3

from pyais.messages import MessageType1, MessageType5, MessageType18
from pyais.stream import TCPConnection
from pyais.constants import TurnRate

from spartid_ais import create_app
from spartid_ais.models import (
    HistoricPositionReport,
    ImoVesselCodes,
    LastPositionReport,
    db,
)

logger = logging.getLogger(__name__)


def create_lastposition(ais_msg: MessageType1 | MessageType18):
    return LastPositionReport(
        mmsi=ais_msg.mmsi,
        lat=ais_msg.lat,
        long=ais_msg.lon,
        speed=ais_msg.speed,
        course=ais_msg.course,
        heading=ais_msg.heading,
        timestamp=datetime.utcnow(),
    )


def create_historicposition(ais_msg: MessageType1):
    if isinstance(ais_msg.turn, TurnRate):
        turn_rate = ais_msg.turn.value
    else:
        turn_rate = ais_msg.turn
    return HistoricPositionReport(
        msg_type=ais_msg.msg_type,
        repeat=ais_msg.repeat,
        mmsi=ais_msg.mmsi,
        status=ais_msg.status,
        turn=turn_rate,
        speed=ais_msg.speed,
        accuracy=ais_msg.accuracy,
        lat=ais_msg.lat,
        long=ais_msg.lon,
        course=ais_msg.course,
        heading=ais_msg.heading,
        maneuver=ais_msg.maneuver,
        raim=ais_msg.raim,
        radio=ais_msg.radio,
        timestamp=datetime.utcnow(),
    )


def create_imovesselcode(ais_msg: MessageType5):
    return ImoVesselCodes(
        mmsi=ais_msg.mmsi,
        imo=ais_msg.imo,
        name=ais_msg.shipname,
        flag="",
        type=ais_msg.ship_type,
    )


KYSTINFO_HOST = "153.44.253.27"
KYSTINFO_PORT = 5631
BUFFER_SIZE = 1024
LOG_STATS_FREQ_S = 60


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        last_logging = datetime.utcnow() - timedelta(seconds=LOG_STATS_FREQ_S - 5)
        num_msgs = 0
        while True:
            for msg in TCPConnection(KYSTINFO_HOST, KYSTINFO_PORT):
                try:
                    decoded_message = msg.decode()
                    utc_now = datetime.utcnow()
                    logger.debug("decoded: {}".format(decoded_message))

                    num_msgs += 1
                    if (utc_now - last_logging).seconds >= LOG_STATS_FREQ_S:
                        logging.info("Number of msgs: {}".format(num_msgs))
                        last_logging = utc_now
                        num_msgs = 0

                    if decoded_message.msg_type in [1, 2, 3]:
                        last_postion = create_lastposition(decoded_message)
                        db.session.merge(last_postion)

                        historic_position = create_historicposition(decoded_message)
                        db.session.add(historic_position)
                        db.session.commit()
                    elif decoded_message.msg_type in [5]:
                        imovessel_code = create_imovesselcode(decoded_message)
                        db.session.merge(imovessel_code)
                        db.session.commit()
                    else:
                        pass
                        # logger.warning(
                        #    "Not expected message type %s", decoded_message
                        # )
                except sqlite3.OperationalError:
                    logger.warn("Database Operational Error.")
