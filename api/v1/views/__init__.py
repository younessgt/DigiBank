from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1', template_folder='../../../web_dynamic/templates')

from api.v1.views.users import *
