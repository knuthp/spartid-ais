import datetime
import os
from logging.config import dictConfig

from flask import Flask, abort, jsonify, send_from_directory

from spartid_ais.aismodel import (
    HistoricPositionReport,
    ImoVesselCodes,
    LastPositionReport,
    db,
)
from spartid_ais.aisschema import ma

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///aisrt.db"
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)
    return app


app = create_app()


@app.route("/")
def hRoot():
    return send_from_directory("static", "leaflet.html")


def _last_position_report_2_geojson(x):
    return {
        "type": "Feature",
        "properties": {
            "mmsi": x.mmsi,
            "course": x.course,
            "heading": x.heading,
            "speed": x.speed,
            "timestamp": x.timestamp,
        },
        "geometry": {"type": "Point", "coordinates": [x.long, x.lat]},
    }


@app.route("/api/tracks")
def aTracks():
    six_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
    tracks = LastPositionReport.query.filter(
        LastPositionReport.timestamp > six_hours_ago
    ).all()
    print("Current number of tracks: {}".format(len(tracks)))
    geojson_features = [_last_position_report_2_geojson(x) for x in tracks]
    return jsonify({"type": "FeatureCollection", "features": geojson_features})


@app.route("/api/tracks/<mmsi>")
def aTrack(mmsi):
    track = LastPositionReport.query.filter(
        LastPositionReport.mmsi == int(mmsi)
    ).first()
    if track:
        return jsonify(_last_position_report_2_geojson(track))
    else:
        abort(404)


@app.route("/api/tracks/<mmsi>/history")
def aTrackHistory(mmsi):
    history = HistoricPositionReport.query.filter(
        HistoricPositionReport.mmsi == int(mmsi)
    ).all()
    geojson_coordinates = []
    linestring = []
    lastReport = None
    for x in history:
        if lastReport and x.timestamp > lastReport + datetime.timedelta(minutes=30):
            if linestring:
                geojson_coordinates.append(linestring)
            linestring = []
        lastReport = x.timestamp
        linestring.append([x.long, x.lat])
    geojson_coordinates.append(linestring)
    return jsonify(
        {
            "type": "Feature",
            "geometry": {"type": "MultiLineString", "coordinates": geojson_coordinates},
        }
    )


@app.route("/api/tracks/<mmsi>/details")
def aTrackDetails(mmsi):
    imoVesselCodes = ImoVesselCodes.query.filter(
        ImoVesselCodes.mmsi == str(mmsi)
    ).first()
    return jsonify(
        {
            "imo": imoVesselCodes.imo,
            "name": imoVesselCodes.name,
            "flag": imoVesselCodes.flag,
            "type": imoVesselCodes.type,
        }
    )


if __name__ == "__main__":
    app.run("0.0.0.0")
