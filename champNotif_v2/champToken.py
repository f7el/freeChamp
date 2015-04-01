__author__ = 'Paul'
from database import query_db, get_db
from flask import g
from utility import genRandomString


   #helper method to get a token for a given email
def _getToken(self, email):
    t = (email,)
    (token,) = query_db('SELECT token FROM verification WHERE email=?', t, one=True)
    return token


def tokenIsAlive(self,token):
    t = (token,)
    (timeStamp,) = query_db('SELECT timestamp FROM VERIFICATION WHERE token=?', t, one=True)
    t = (timeStamp,)
    #result is 1 if time is less than 48 hrs. else result is 0
    (isExpired,) = query_db("SELECT cast((strftime('%s','now','localtime')- strftime('%s',?)) AS real)/60/60 < 48.00",
                            t, one=True)
    return isExpired == 1

def genNewToken(self,email):
    g.db = get_db()
    newToken = self.genRandomString()
    token = self._getToken(email)
    t = (newToken,token)
    g.db.execute('UPDATE verification SET token=?, timestamp=datetime("now","localtime") WHERE token=?', t)
    g.db.commit()
    return newToken

def tokenExists(email):
    t = (email,)
    (exists,) = query_db("SELECT COUNT(token) FROM VERIFICATION WHERE token=?", t, one=True)
    return exists == 1

def getEmailFromToken(token):
    t = (token,)
    (email,) = query_db("SELECT email FROM VERIFICATION WHERE token=?",t,one=True)
    return email