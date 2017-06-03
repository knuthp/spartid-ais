import datetime
import json
import socket

import ais.compatibility.gpsd
import ais.stream
from aismodel import db, HistoricPositionReport, LastPositionReport, ShipDetails
from aisapp import create_app


def create_lastposition(ais_msg):
    return LastPositionReport(
        mmsi=ais_msg['mmsi'],
        lat=ais_msg['x'], 
        long=ais_msg['y'], 
        speed=ais_msg['sog'], 
        course=ais_msg['cog'], 
        heading=ais_msg['true_heading'],
        timestamp=datetime.datetime.utcnow())
    
def create_historicposition(ais_msg):
    return HistoricPositionReport(
        mmsi=ais_msg['mmsi'], 
        lat=ais_msg['x'], 
        long=ais_msg['y'], 
        timestamp=datetime.datetime.utcnow())
    

KYSTINFO_HOST = '153.44.253.27'
KYSTINFO_PORT = 5631
BUFFER_SIZE = 1024 



if __name__ == '__main__':
    app = create_app()
    with app.app_context():
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((KYSTINFO_HOST, KYSTINFO_PORT))
        f = s.makefile()
        
        pos_map = {}
        msg_type = {}
        for msg in ais.stream.decode(f):
#            print('id:{id:2}, msg: {msg}'.format(id=msg['id'], msg=msg))
            count = msg_type[msg['id']]['count'] + 1 if msg['id'] in msg_type else 0
            msg_type[msg['id']] = {'count' : count, 'last' : msg}
            if msg['id'] in [1, 3]:
                last_postion = create_lastposition(msg)
                db.session.merge(last_postion)
                pos_map[msg['mmsi']] = msg
                
                historic_position = create_historicposition(msg)
                db.session.add(historic_position)
        #        print("{id}, {mmsi}, {size:06d}, {rows:06d}".format(id=msg['id'], mmsi=msg['mmsi'], size=len(pos_map), rows=session.query(LastPositionReport).count()))
        #        print('nmea: {}'.format(msg))
        #        print('deco: {}'.format(msg))
        #        gpsdmsg = ais.compatibility.gpsd.mangle(msg)
        #        print('gpsd: {}'.format(json.dumps(gpsdmsg, )))
                db.session.commit()
            elif msg['id'] in [19, 21]: #, 24]:
                ship_details = ShipDetails(
                    mmsi=msg['mmsi'],
                    name=msg['name'].strip('@'))
                db.session.merge(ship_details)
                db.session.commit()
        s.close()
    
