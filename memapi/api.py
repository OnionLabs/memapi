from flask import Blueprint, request
from memapi import service_list
from memapi.utils import get_allowed_args

blueprint = Blueprint("api", __name__, url_prefix="/api/")

services = {svc.SERVICE_DOMAIN: svc for svc in service_list()}


@blueprint.route("/")
def index():
    listing = {}
    for domain, obj in services.items():
        svc = obj()
        listing[svc.SERVICE_NAME] = {
            "domain": svc.SERVICE_DOMAIN,
            "allowed_actions": {
                action: get_allowed_args(getattr(svc, f"action_{action}")) for action in svc.allowed_actions
            },
        }

        return {"available_services": listing}


@blueprint.route("/<service_name>/<action>/")
def execute(service_name, action):
    current = services.get(service_name)
    if not current:
        raise ModuleNotFoundError(f"{service_name} doesn't exist")

    return current().action(action, **request.args)
