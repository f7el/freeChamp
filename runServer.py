__author__ = 'Paul'
from champNotif_v2 import app
app.secret_key = app.config['SECRET_KEY']
app.run(host=app.config['HOST'], port=app.config['PORT'], debug=True)