import pandas as pd
from flask import Blueprint, render_template

from spartid_ais import db

bp = Blueprint("dataexplore", __name__)


@bp.route("/simplestats")
def simple_stats():
    return "TBD"


@bp.route("/vessels/<int:mmsi>/travel")
def vessel_travel(mmsi):
    df_travel_raw = pd.read_sql_query(
        """
            SELECT *
            FROM historic_position
            WHERE mmsi = %(mmsi)s AND
                timestamp > now() - interval '3 day';
        """,
        db.engine,
        params={"mmsi": mmsi},
    )
    return render_template("vessel_travel.html.j2", datatable=df_travel_raw.to_html())


@bp.route("/vessels")
def known_vessels():
    df_raw_imo_vessels = pd.read_sql("SELECT * from imo_vessel_codes", db.engine)
    return render_template(
        "vessels.html.j2",
        datatable=df_raw_imo_vessels.to_html(
            classes=["table table-bordered", "table-striped", "table-hover"]
        ),
    )
