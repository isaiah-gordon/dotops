from flask import Blueprint

main = Blueprint('main', __name__)
train = Blueprint('train', __name__)

from . import api, website
