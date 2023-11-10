import datetime

from flask import abort, jsonify, render_template, Blueprint
from spartid_ais.models import (
    HistoricPositionReport,
    ImoVesselCodes,
    LastPositionReport,
)


bp = Blueprint("views", __name__)


@bp.route("/")
def hRoot():
    return render_template("leaflet.html.j2")


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


@bp.route("/api/tracks")
def aTracks():
    six_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
    tracks = LastPositionReport.query.filter(
        LastPositionReport.timestamp > six_hours_ago
    ).all()
    print("Current number of tracks: {}".format(len(tracks)))
    geojson_features = [_last_position_report_2_geojson(x) for x in tracks]
    return jsonify({"type": "FeatureCollection", "features": geojson_features})


@bp.route("/api/tracks/<mmsi>")
def aTrack(mmsi):
    track = LastPositionReport.query.filter(
        LastPositionReport.mmsi == int(mmsi)
    ).first()
    if track:
        return jsonify(_last_position_report_2_geojson(track))
    else:
        abort(404)


@bp.route("/api/tracks/<mmsi>/history")
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


@bp.route("/api/tracks/<mmsi>/details")
def aTrackDetails(mmsi):
    imoVesselCodes = ImoVesselCodes.query.filter(
        ImoVesselCodes.mmsi == str(mmsi)
    ).first()
    if imoVesselCodes is None:
        return jsonify({"error": "Not found"})
    return jsonify(
        {
            "imo": imoVesselCodes.imo,
            "name": imoVesselCodes.name,
            "flag": imoVesselCodes.flag,
            "type": imoVesselCodes.type,
        }
    )
