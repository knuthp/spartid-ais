from flask import Flask, jsonify, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy

from aismodel import db, LastPositionReport, HistoricPositionReport
from aisschema import ma, LastPositionReportSchema




def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aisrt.db'
    db.init_app(app)
    ma.init_app(app)
    return app

app = create_app()



@app.route('/')
def hRoot():
    return send_from_directory('static', 'leaflet.html')

def _last_position_report_2_geojson(x):
    return {'type' : 'Feature', 
            'properties' : { 
                'mmsi' : x.mmsi, 
                'course' :  x.course, 
                'heading' : x.heading, 
                'speed' : x.speed, 
                'timestamp' : x.timestamp }, 
            'geometry' : {
                'type' : 'Point', 
                'coordinates' : [x.lat, x.long]
                }
            }

@app.route('/api/tracks')
def aShips():
    tracks = LastPositionReport.query.all()
    geojson_features = [_last_position_report_2_geojson(x) for x in tracks]
    return jsonify({'type' : 'FeatureCollection', 'features' : geojson_features})

@app.route('/api/tracks/<mmsi>')
def aShip(mmsi):
    track = LastPositionReport.query.filter(LastPositionReport.mmsi == int(mmsi)).first()
    if track:
        return jsonify(_last_position_report_2_geojson(track))
    else:
        abort(404)

@app.route('/api/tracks/<mmsi>/history')
def aShipHistory(mmsi):
    history =  HistoricPositionReport.query.filter(HistoricPositionReport.mmsi == int(mmsi)).all()
    geojson_coordinates = [[x.lat, x.long] for x in history]
    return jsonify({'type' : 'Feature', 'geometry' : {'type' : 'LineString', 'coordinates' : geojson_coordinates}})

if __name__ == '__main__':
    app.run('0.0.0.0')