import datetime
from datetime import timezone
from urllib.parse import urlparse

import duckdb
from flask import Blueprint, abort, current_app, jsonify, render_template, request
from shapely.geometry import shape

from spartid_ais import settings
from spartid_ais.models import (
    HistoricPositionReport,
    ImoVesselCodes,
    LastPositionReport,
)

bp = Blueprint("views", __name__)

@bp.route("/")
def root():
    return render_template("leaflet.html.j2", map=settings.map)


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
def tracks():
    six_hours_ago = datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=6)
    tracks = LastPositionReport.query.filter(
        LastPositionReport.timestamp > six_hours_ago
    ).all()
    print("Current number of tracks: {}".format(len(tracks)))
    geojson_features = [_last_position_report_2_geojson(x) for x in tracks]
    return jsonify({"type": "FeatureCollection", "features": geojson_features})


@bp.route("/api/tracks/within_geojson", methods=["POST"])
def tracks_within_geojson():
    constring = current_app.config["SQLALCHEMY_DATABASE_URI"]
    con_splitted = urlparse(constring)
    geojson_data = request.json
    con = duckdb.connect()
    for ext in ["postgres", "spatial"]:
        con.install_extension(ext)
        con.load_extension(ext)
    con.sql(f"""
        ATTACH 'dbname=spartid_ais
            user={con_splitted.username}
            password={con_splitted.password}
            host={con_splitted.hostname}'
        AS db (TYPE postgres);
    """)
    feature = geojson_data
    areas = [shape(x["geometry"]) for x in feature["features"]]

    multi_intersects = " OR ".join(["ST_INTERSECTS(geom, (?))" for _ in areas])
    # Execute the SQL query to
    query = f"""
    SELECT *, ST_POINT(long, lat) as geom, datediff('hour', now() AT TIME ZONE 'UTC', timestamp)
    FROM db.public.last_position
    WHERE ({multi_intersects}) AND datediff('hour', now()::timestamp, timestamp) > -6
    """

    df = con.execute(query, [area.wkt for area in areas]).df()
    ret = []
    for _, row in df.iterrows():
        ret.append({
            "type": "Feature",
            "properties": {
                "mmsi": row["mmsi"],
                "course": row["course"],
                "heading": row["heading"],
                "speed": row["speed"],
                "timestamp": row["timestamp"],
            },
            "geometry": {"type": "Point", "coordinates": [row["long"], row["lat"]]},
        })
    return jsonify({"type": "FeatureCollection", "features": ret})


@bp.route("/api/tracks/<mmsi>")
def tracks_mmsi(mmsi):
    track = LastPositionReport.query.filter(
        LastPositionReport.mmsi == int(mmsi)
    ).first()
    if track:
        return jsonify(_last_position_report_2_geojson(track))
    else:
        abort(404)


@bp.route("/api/tracks/<mmsi>/history")
def track_mmsi_history(mmsi):
    history = HistoricPositionReport.query.filter(
        HistoricPositionReport.mmsi == int(mmsi)
    ).all()
    geojson_coordinates = []
    linestring = []
    last_report = None
    for x in history:
        if last_report and x.timestamp > last_report + datetime.timedelta(minutes=30):
            if linestring:
                geojson_coordinates.append(linestring)
            linestring = []
        last_report = x.timestamp
        linestring.append([x.long, x.lat])
    geojson_coordinates.append(linestring)
    return jsonify(
        {
            "type": "Feature",
            "geometry": {"type": "MultiLineString", "coordinates": geojson_coordinates},
        }
    )


@bp.route("/api/tracks/<mmsi>/details")
def track_mmsi_details(mmsi):
    imo_vessel_codes = ImoVesselCodes.query.filter(
        ImoVesselCodes.mmsi == str(mmsi)
    ).first()
    if imo_vessel_codes is None:
        return jsonify({"error": "Not found"})
    return jsonify(
        {
            "imo": imo_vessel_codes.imo,
            "name": imo_vessel_codes.name,
            "flag": imo_vessel_codes.flag,
            "type": imo_vessel_codes.type,
        }
    )
