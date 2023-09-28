# Simple AIS example with data from Kystverket
[Norwegian Kystverket](http://kystverket.no) publish AIS data for ship positions that can be used under [NLOD license](https://data.norge.no/nlod/no/1.0). This application stores the positions received and present current situation and history in a Map using [Leaflet](http://http://leafletjs.com).

# Technology
This demo is made using Python with Flask for the web server part, Leaflet/HTML for the presentation and SQLite for the database. AIS position data is read from a TCP connection continously using Python library [pyais](https://github.com/M0r13n/pyais) . The position updates are stored in a SQLite database using two tables: LastPositionReport and HistoricPosition. In addition a mapping table from mmsi to IMO data are imported into ImoVesselCodes table.

# Example
![Map](docs/AIS_history.png)
