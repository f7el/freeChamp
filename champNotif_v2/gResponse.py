__author__ = 'Paul'
#this module sends the gresponse from the captcha to google for verification
import requests
from champNotif_v2 import app


def isVerified(gResponseVal):
    gPostUrl = "https://www.google.com/recaptcha/api/siteverify"
    secret = app.config['CAPTCHA_SECRET']
    jsonObj = requests.post(gPostUrl, {'secret': secret, 'response': gResponseVal})
    response = jsonObj.json()
    return response['success']