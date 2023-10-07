from spartid_ais import ma


class LastPositionReportSchema(ma.Schema):
    class Meta:
        # TODO Why does not model work for this?
        # model = LastPositionReport
        fields = ("mmsi", "lat", "long", "speed", "course", "heading", "timestamp")
