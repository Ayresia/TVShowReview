from flask import Blueprint

show = Blueprint("show", __name__, url_prefix="/show")

from . import views
