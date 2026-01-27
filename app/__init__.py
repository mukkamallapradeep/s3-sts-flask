import os
from flask import Flask

from app.config import Config
from app.logging_config import configure_logging
from app.routes.api import api
from app.routes.views import views
from app.services.aws_clients import STSSessionCache

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app_config = Config()
    app.config.from_object(app_config)

    # Logging
    configure_logging(app_config.LOG_DIR, app_config.LOG_LEVEL)

    # STS cache
    app.config["STS_CACHE"] = STSSessionCache(app_config)

    # Flask settings
    app.secret_key = app_config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = app_config.MAX_CONTENT_LENGTH

    # Blueprints
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(views)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app

# For 'flask run' support
app = create_app()
