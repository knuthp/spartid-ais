import json
import socket

import ais.compatibility.gpsd
import ais.stream

KYSTINFO_HOST = '153.44.253.27'
KYSTINFO_PORT = 5631
BUFFER_SIZE = 1024 

if __name__ == '__main__':    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((KYSTINFO_HOST, KYSTINFO_PORT))
    f = s.makefile()
    
    for msg in ais.stream.decode(f):
        print('nmea: {}'.format(msg))
        print('deco: {}'.format(msg))
        gpsdmsg = ais.compatibility.gpsd.mangle(msg)
        print('gpsd: {}'.format(json.dumps(gpsdmsg, )))
    s.close()
    
