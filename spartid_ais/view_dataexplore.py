from flask import Blueprint, render_template
import pandas as pd
from spartid_ais import db

bp = Blueprint("dataexplore", __name__)


@bp.route("/simplestats")
def simple_stats():
    df_raw_imo_vessels = pd.read_sql("SELECT * from imo_vessel_codes", db.engine)
    return render_template(
        "statistics.html.j2",
        datatable=df_raw_imo_vessels.to_html(
            classes=["table table-bordered", "table-striped", "table-hover"]
        ),
    )
