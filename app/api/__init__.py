from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

from .account import register_account_resources
from .admin import register_admin_resources


def register_all_resources():
    register_account_resources(api)
    register_admin_resources(api)


register_all_resources()
