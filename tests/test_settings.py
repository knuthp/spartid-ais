from spartid_ais.settings import Settings


def test_default():
    settings = Settings()
    default_zoom = 11
    assert settings.map.zoom == default_zoom
