from spartid_ais.settings import Settings


def test_default():
    settings = Settings()
    assert settings.map.zoom == 11