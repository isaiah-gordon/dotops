from flask import Blueprint

main = Blueprint('main', __name__)
interface = Blueprint('interface', __name__)

from . import api, website, events
