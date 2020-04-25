import logging

from memapi.services import ServiceProvider

from flask import Flask, logging as flasklogging

from memapi.utils import get_classes_for_path

log = logging.getLogger(__name__)
log.addHandler(flasklogging.default_handler)


def create_app():
    app = Flask(__name__)

    if app.debug:
        log.setLevel(logging.DEBUG)

    register_blueprints(app)

    return app


def register_blueprints(app: Flask):
    from .api import blueprint as api_blueprint

    app.register_blueprint(api_blueprint)


def service_list():
    enabled_services: list = ["memapi.services.repostuj"]
    found_services = []

    for path in enabled_services:
        for svc in get_classes_for_path(path, ServiceProvider):
            found_services.append(svc)

    return found_services
