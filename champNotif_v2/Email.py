__author__ = 'StormCrow'

from flask import g
from champNotif_v2 import app
import sqlite3, os, hashlib, smtplib
from database import get_db,query_db
from token import *
from info import *

from email.mime.text import MIMEText

class Email:

    __email__ = None
    __emailId__ = None



    def addEmail(self, email, password, salt, isVerified):
        t = (email, password, salt, isVerified)
        g.db.execute('INSERT INTO USERS VALUES (?,?,?,?)',t)
        g.db.commit()
        #newId = cur.lastrowid

        #return newId

    #register is a boolean. true means i can set the count to 0
    def addVerification(self, email, token):
        db = get_db()
        dt = query_db("SELECT datetime('now','localtime')",one=True)
        t = (token,dt[0],email)
        db.execute("INSERT INTO VERIFICATION values(?,?,'0',?)",t)
        self.updateVerificationCount(email,1)
        g.db.commit()

    def emailExists(self, email):
        t = (email,)
        result = query_db('SELECT COUNT(email) FROM USERS WHERE email=(?)',t,one=True)
        count = result[0]
        print "count: " + str(count)
        if count > 0:
            return True
        return False

    def makeEmailActive(self,email):
        g.db = get_db()
        t = (email,)
        g.db.execute('UPDATE USERS SET isVerified=1 WHERE email=?',t)
        g.db.commit()

    def sendVerificationEmail(self, email, token):
        notificationEmail = app.config['NOTIFICATIONEMAIL']
        emailPw = app.config['EMAILPW']
        server = app.config['SERVER']
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(notificationEmail, emailPw)

        msg = MIMEText("Click the link to confirm your e-mail \n\n" + "http://" + str(app.config['SERVER']) + \
                       "/verifyEmail?token="+token)
        msg['To'] = email
        msg['From'] =notificationEmail
        msg['Subject'] = 'email verification'
        try:
            server.sendmail(notificationEmail, email, msg.as_string())
        finally:
            server.quit()

    def resetVerificationCount(self, email):
        g.db = get_db()
        t = (email,)
        g.db.execute('UPDATE verification SET count=0 WHERE email=?',t)
        g.db.commit()

    def updateVerificationCount(self, email, count):
        t = (count, email)
        g.db = get_db()
        g.db.execute('UPDATE verification SET count=? WHERE email=?',t)
        g.db.commit()

    def getCount(self, email):
        t = (email,)
        (count,) = query_db('SELECT count FROM verification WHERE email=?',t,one=True)
        return count

    def verificationFromToday(self, email):
         g.db = get_db()
         t = (email,)
         result = query_db("SELECT count(strftime('%Y-%m-%d',timestamp,'localtime')) from verification WHERE strftime(" + \
                          "'%Y-%m-%d',timestamp,'localtime')=strftime('%Y-%m-%d','now','localtime') and email=?",t,one=True)
         count = result[0]
         return count == 1


     #returns true if send limit has not been exceeded for a given email
    def checkSendLimit(self, email):
        emailLib = Email()
        if emailLib.emailExists(email):
            token = self._getToken(email)
            if self.tokenIsAlive(token):
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




