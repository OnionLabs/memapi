from flask import Blueprint, request
from memapi import service_list
from memapi.utils import get_allowed_args

blueprint = Blueprint("api", __name__, url_prefix="/api/")

services = {svc().service_slug: svc for svc in service_list()}


@blueprint.route("/")
def index():
    listing = {}
    for domain, obj in services.items():
        svc = obj()
        listing[svc.service_slug] = {
            "domain": svc.service_url,
            "slug": svc.service_slug,
            "allowed_actions": {
                action: get_allowed_args(getattr(svc, f"action_{action}"))
                for action in svc.allowed_actions
            },
        }

        return {"available_services": listing}


@blueprint.route("/<service_slug>/")
def help(service_slug):
    current = services.get(service_slug)
    if not current:
        raise ModuleNotFoundError(f"{service_slug} doesn't exist")

    svc = current()

    return {
        "domain": svc.service_url,
        "slug": svc.service_slug,
        "allowed_actions": {
            action: get_allowed_args(getattr(svc, f"action_{action}"))
            for action in svc.allowed_actions
        },
    }


@blueprint.route("/<service_slug>/<action>/", methods=['POST'])
def execute(service_slug, action):
    current = services.get(service_slug)
    if not current:
        raise ModuleNotFoundError(f"{service_slug} doesn't exist")

    return current().action(action, **request.json).as_dict
