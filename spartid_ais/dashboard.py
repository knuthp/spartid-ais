from os import environ
import folium
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from streamlit_folium import folium_static
from spartid_ais.tracksymbol2 import TrackSymbol2

st.title("Streamlit")

db_uri = environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql://postgres:postgres@localhost:5432/spartid_ais",
)
engine = create_engine(db_uri)


# st.header("Vessels")
# st.dataframe(pd.read_sql("SELECT * FROM imo_vessel_codes", engine))

# st.header("Currentpos")
# st.dataframe(pd.read_sql("SELECT * FROM last_position", engine))

st.header("Vessels")
df_vessels = pd.read_sql(
    """
        SELECT
            timestamp,
            imo_vessel_codes.mmsi,
            imo,
            name,
            speed,
            course,
            heading,
            lat,
            long
        FROM
            imo_vessel_codes
        LEFT JOIN last_position
            ON last_position.mmsi = imo_vessel_codes.mmsi
        WHERE DATE_PART('Day',now() - timestamp::timestamptz) < 1
        ORDER BY timestamp
        ;
    """,
    engine,
)
m = folium.Map(location=[59.824713, 10.456367], zoom_start=11)
df_vessels_display = (
    df_vessels.query("lat.notnull()").query("long.notnull()")
    #        .head(10)
)

for _, vessel in df_vessels_display.iterrows():
    TrackSymbol2(
        location=(vessel["lat"], vessel["long"]),
        heading=vessel["heading"],
        course=vessel["course"],
        speed=vessel["speed"],
        mmsi=vessel["mmsi"],
        timestamp=vessel["timestamp"],
        popup=f"mmsi: {vessel['mmsi']}, name: {vessel['name']}",
    ).add_to(m)

st_data = folium_static(m, width=725)

st.dataframe(df_vessels_display)
