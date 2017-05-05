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

@app.route('/api/tracks')
def aShips():
    tracks = LastPositionReport.query.all()
    tracks_json = LastPositionReportSchema().dump(tracks, many=True)
    return jsonify({'_meta' : { 'size' : len(tracks) }, 'data' : tracks_json})

if __name__ == '__main__':
    app.run('0.0.0.0')