__author__ = 'Paul'
from champNotif_v2 import app
app.secret_key = app.config['SECRET_KEY']
app.run(debug=True)