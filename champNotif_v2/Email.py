__author__ = 'StormCrow'

from flask import g
from champNotif_v2 import app
import sqlite3, os, hashlib, smtplib
from database import get_db,query_db

from info import *

from email.mime.text import MIMEText

class Email:

    __email__ = None
    __emailId__ = None

    #helper method to get a token for a given email
    def _getToken(self, email):
        t = (email,)
        result = query_db('SELECT token FROM verification WHERE email=?',t,one=True)
        return result['token']

    def addEmail(self, email, password, salt, isVerified):
        t = (email, password, salt, isVerified)
        g.db.execute('INSERT INTO USERS VALUES (?,?,?,?)', t)
        #newId = cur.lastrowid

        #return newId

    def addVerification(self, email):

    def emailExists(self, email):
        db = get_db()
        t = (email,)
        result = query_db('SELECT COUNT(email) FROM USERS WHERE email=(?)',t,one=True)
        count = result[0]
        if count > 0:
            return True

        return False

    def exceededDailyVerificationCount(self,email):
        db = get_db()
        t = (email,)


        get_db('SELECT COUNT(email) FROM verification WHERE email=? and ')

    def makeEmailActive(self,email):
        con = sqlite3.connect(database)
        t = (email,)

        with con:
            cur = con.cursor()
            cur.execute('UPDATE USERS SET isVerified=1 WHERE email=?',t)

    def genRandomString(self):
        randomBytes = os.urandom(32)
        hash = hashlib.sha512()
        hash.update(randomBytes)
        return hash.hexdigest()

    def genNewToken(self,email):
        g.db = get_db()
        newToken = self.genRandomString()
        token = self._getToken(email)
        t = (newToken,token)
        g.db.execute('UPDATE verification SET token=?, timestamp=datetime("now","localtime") WHERE token=?',t)
        return newToken

    #returns tuple where first element is bool and 2nd is email if bool is true
    def tokenIsActive(self,token):
        t = (token,)
        result = query_db('SELECT COUNT(*),email FROM verification WHERE token=? and datetime("now","localtime") < datetime(timestamp,"+2 day")',t)
        return result


    def sendVerificationEmail(self, email, token):
        notificationEmail = app.config['NOTIFICATIONEMAIL']
        emailPw = app.config['EMAILPW']
        server = app.config['SERVER']
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(notificationEmail, emailPw)
        #msg = "Click the link to confirm your e-mail \n\n" + server + "/verify?token="+token
        #subject = "email verification"


        #server.sendmail(notificationEmail,email,msg)

        #msg = MIMEText("Click the link to confirm your e-mail \n\n http://www.freechamp.sonyar.info/verify.py?token="+token)
        msg = MIMEText("Click the link to confirm your e-mail \n\n" + server + "/verifyEmail?token="+token)
        msg['To'] = email
        msg['From'] =notificationEmail
        msg['Subject'] = 'email verification'



        try:
            server.sendmail(notificationEmail, email, msg.as_string())
        finally:
            server.quit()


    def verificationFromToday(self, email):
        t = (email,)
        con = sqlite3.connect(database)
        with con:
             c = con.cursor()
             c.execute("SELECT count(strftime('%Y-%m-%d',timestamp,'localtime')) from verification WHERE strftime(" + \
                       "'%Y-%m-%d',timestamp,'localtime')=strftime('%Y-%m-%d','now','localtime') and email=?", t)
             result = c.fetchone()
             count = result[0]
             return count == 1

    def resetVerificationCount(self, email):
        con = sqlite3.connect(database)
        t = (email,)
        with con:
            c = con.cursor()
            c.execute('UPDATE verification SET count=0 WHERE email=?',t)

    def updateVerificationCount(self, email, count):
        con = sqlite3.connect(database)
        t = (count,email)
        with con:
            c = con.cursor()
            c.execute('UPDATE verification SET count=? WHERE email=?',t)

    def getCount(self, email):
        con = sqlite3.connect(database)
        t = (email,)
        with con:
            c = con.cursor()
            c.execute('SELECT count FROM verification WHERE email=?',t)
            result = c.fetchone()
            return result[0]

    #returns true if send limit has not been exceeded for a given email
    def checkSendLimit(self, email):
        emailLib = Email()
        if emailLib.emailExists(email):
        #does the email have a timestamp of today?
            today = self.verificationFromToday(email)
            if today:
                count = self.getCount(email)
                if count == 0:
                    self.updateVerificationCount(email,1)
                    return True
                elif count == 1:
                    self.updateVerificationCount(email,2)
                    return True
                else:
                    return False
        else:
            return False








