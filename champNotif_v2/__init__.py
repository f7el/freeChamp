__author__ = 'Paul'

from flask import Flask
app = Flask(__name__)
app.config.from_pyfile('info.py')

import champNotif_v2.views