from jinja2 import Template
import numpy as np
from folium.elements import JSCSSMixin
from folium.map import Marker
from folium.utilities import parse_options


class TrackSymbol2(JSCSSMixin, Marker):
    """Ship track symbol/marker for folium.

    Based on folium.plugins.boatmarker
    """

    _template = Template(
        """
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = new L.trackSymbol(
                    [{{ this.location[0] }}, {{ this.location[1] }}] , {
                fill: true,
                fillColor: 'yellow',
                fillOpacity: 1,
                heading: {{ this.heading }},
                course: {{ this.course }},
                speed: {{ this.speed }},
            }).addTo({{ this._parent.get_name() }});
        {% endmacro %}
        """
    )

    default_js = [
        (
            "markerclusterjs",
            (
                "https://cdn.jsdelivr.net/gh/org-arl/leaflet-tracksymbol2/"
                "dist/leaflet-tracksymbol2.umd.js"
            ),
        ),
    ]

    def __init__(
        self,
        location,
        popup=None,
        icon=None,
        heading=0,
        course=0,
        speed=0,
        mmsi="",
        timestamp=0,
        **kwargs
    ):
        super().__init__(location, popup=popup, icon=icon)
        self._name = "TrackSymbol2"
        self.heading = self._to_radians(heading)
        self.course = self._to_radians(course)
        self.speed = self._normalize(speed)
        self.mmsi = mmsi
        self.timestamp = timestamp
        self.options = parse_options(**kwargs)

    def _to_radians(self, degs):
        if np.isnan(degs):
            return 0
        return degs * np.pi / 180

    def _normalize(self, speed):
        if np.isnan(speed):
            return 0
        if speed > 100:
            return 100 / 1.944
        return speed / 1.944
