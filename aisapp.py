from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from aismodel import db, LastPositionReport
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
    return "Hello"

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

if __name__ == '__main__':
    app.run('0.0.0.0')