from datetime import datetime, timedelta
import json
import logging
import socket
import sys
import time

import ais.compatibility.gpsd
import ais.stream
from spartid_ais.aismodel import ImoVesselCodes, db, HistoricPositionReport, LastPositionReport
from spartid_ais.aisapp import create_app


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


def readlines(sock, recv_buffer=4096, delim='\n'):
	buffer = ''
	data = True
	while data:
		data = sock.recv(recv_buffer).decode()
		buffer += data

		while buffer.find(delim) != -1:
			line, buffer = buffer.split('\n', 1)
			yield line
	return


def read_raw(generator):
    stack = [[] for _ in range(10)]
    for line in generator:
        values = line.split(',')
        if len(values) == 7:
            packet_type, count, fragment_no, seq_id, radio_channel, payload, fill_bits_checksum = values
        elif len(values) == 8:
            num, packet_type, count, fragment_no, seq_id, radio_channel, payload, fill_bits_checksum = values
        else:
            logger.error("Could not unpack line into 7 elements %s", line)
            continue
        count = int(count)
        fragment_no = int(fragment_no)
        seq_id = int(seq_id) if seq_id else None
        fill_bits = int(fill_bits_checksum[0])

        if count == 1:
            try:
                ais_msg = ais.decode(payload, 0)
            except:
                logger.exception("Failed to decode sinlge message last_line=%s", line)
                continue
        else:
            stack[seq_id].append(payload)
            if fragment_no < count:
                continue
            elif fragment_no == count:
                total_payload = "".join(stack[seq_id])
                stack[seq_id] = []
                try:
                    ais_msg = ais.decode(total_payload, fill_bits)
                except Exception as e:
                    logger.exception("Failed to decode fragmented message. total_payload=%s, fill_bits=%s, last_line=%s",
                        total_payload, fill_bits, line)
                    continue
#        logger.debug("id:{id}, mmsi:{mmsi},".format(**ais_msg))
        if ais_msg is not None:
            return ais_msg
        else:
            logger.warning("Got an empty ais message: %s", line)


def create_lastposition(ais_msg):
    return LastPositionReport(
        mmsi=ais_msg['mmsi'],
        lat=ais_msg['lat'], 
        long=ais_msg['lon'], 
        speed=ais_msg['speed'], 
        course=ais_msg['course'], 
        heading=ais_msg['heading'],
        timestamp=datetime.utcnow())
    

def create_historicposition(ais_msg):
    return HistoricPositionReport(
        mmsi=ais_msg['mmsi'], 
        lat=ais_msg['lat'], 
        long=ais_msg['lon'], 
        timestamp=datetime.utcnow())


def create_imovesselcode(ais_msg):
    return ImoVesselCodes(
        mmsi=ais_msg["mmsi"],
        imo=ais_msg["imo_num"],
        name=ais_msg["name"].strip("@").strip(),
        flag="",
        type=ais_msg["type_and_cargo"],
    )    

KYSTINFO_HOST = '153.44.253.27'
KYSTINFO_PORT = 5631
BUFFER_SIZE = 1024
LOG_STATS_FREQ_S = 60



if __name__ == '__main__':
    app = create_app()
    with app.app_context():
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((KYSTINFO_HOST, KYSTINFO_PORT))
        s.settimeout(20)
        last_logging = datetime.utcnow() - timedelta(seconds=LOG_STATS_FREQ_S - 5)

        generator = readlines(s)
        num_msgs = 0
        while True:
            try:
                ais_msg = read_raw(generator)
                # logger.debug("id:{id}, mmsi:{mmsi},".format(**ais_msg))
                gpsdmsg = ais.compatibility.gpsd.mangle(ais_msg)

                utc_now = datetime.utcnow()
                gpsdmsg['timestamp'] = utc_now
                logger.debug('gpsd: {}'.format(gpsdmsg))

                num_msgs += 1
                if (utc_now - last_logging).seconds >= LOG_STATS_FREQ_S:
                    logging.info("Number of msgs: {}".format(num_msgs))
                    last_logging = utc_now
                    num_msgs = 0

                if ais_msg['id'] in [3]: # [1, 3]:
                    last_postion = create_lastposition(gpsdmsg)
                    db.session.merge(last_postion)
                    # pos_map[msg['mmsi']] = msg
                    
                    historic_position = create_historicposition(gpsdmsg)
                    db.session.add(historic_position)
                    db.session.commit()
                elif ais_msg['id'] in [5]:
                    imovessel_code = create_imovesselcode(ais_msg)
                    db.session.merge(imovessel_code)                    
                    db.session.commit()
                else:
                    pass
                    # logger.warning("Not expected message type %s", ais_msg)

            except socket.timeout:
                logger.exception("Socket timed out, try to reconnect...")
                while True:
                    try:
                        s.close()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((KYSTINFO_HOST, KYSTINFO_PORT))
                        s.settimeout(2)
                        generator = readlines(s)
                        break
                    except socket.error:
                        logger.exception("Failed to reconnect, retrying")
                        time.sleep(10.0)


        s.close() 
