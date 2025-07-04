"""Settings that can be set at startup to configure spartid-ais.

Uses pydantic that supports environment variables and settings json file.
Moving center of map and zoom level.
```bash
export MAP__ZOOM=16
export MAP__CENTER__LONG=10.611268532369081
export MAP__CENTER__LAT=59.669607206900906
```
"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class PositionSettings(BaseModel):
    lat: float
    long: float


class MapSettings(BaseModel):
    """Settings for viewport of map on base page"""

    center: PositionSettings = PositionSettings(lat=59.824713, long=10.456367)
    zoom: int = 11


class Settings(BaseSettings):
    map: MapSettings = MapSettings()
    model_config = SettingsConfigDict(env_nested_delimiter="__")
