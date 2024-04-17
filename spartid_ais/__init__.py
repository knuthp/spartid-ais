import logging
import os
from logging.config import dictConfig

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from spartid_ais.settings import Settings

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
bootstrap = Bootstrap5()
settings = Settings()
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///aisrt.db"
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)

    # Blueprints
    from spartid_ais.view_dataexplore import bp as dataexplore_bp
    from spartid_ais.views import bp as errors_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(dataexplore_bp)

    logger.info("Url maps %s", app.url_map)
    return app
