import os

from slugify import slugify
from flask import Flask
from flask.ext.assets import Environment
from flask_frozen import Freezer

from opented import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
assets = Environment(app)
freezer = Freezer(app)
