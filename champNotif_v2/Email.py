__author__ = 'StormCrow'

from flask import g, abort
from champNotif_v2 import app
import sqlite3, os, hashlib, smtplib
from database import get_db,query_db
from champToken import *
from info import *
from logging import FileHandler
from logging import Formatter
import logging


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#provides opt-out msg for the email defs. isHTML is a bool that helpers determine what type of msg to return (plain or html)
#token is the unique identifier for a user
def getOptOutMessage(token, isHTML=False):
    if not isHTML:
        optOutMsg = "\n\nhttp://" + app.config['HOST'] + ":" + str(app.config['PORT']) + "/optOut>opt-out?token=" + token
    else:
        optOutMsg = "<br/><br/><a href=http://" + app.config['HOST'] + ":" + str(app.config['PORT']) + "/optOut>opt-out?token=" + token + "</a>"

    return optOutMsg

def addEmail( email, password, salt, isVerified):
    t = (email, password, salt, isVerified)
    g.db.execute('INSERT INTO USERS VALUES (?,?,?,?)', t)
    g.db.commit()
    #newId = cur.lastrowid

    #return newId

#register is a boolean. true means i can set the count to 0
def addVerification( email, token):
    db = get_db()
    dt = query_db("SELECT datetime('now','localtime')",one=True)
    t = (token,dt[0],email)
    db.execute("INSERT INTO VERIFICATION values(?,?,'0',?)",t)
    updateVerificationCount(email,1)
    g.db.commit()

#updates timestamp and count for verification
def refreshVerification(email):
    db = get_db()
    dt = query_db("SELECT datetime('now','localtime')",one=True)
    t = (dt[0],email)
    db.execute("UPDATE VERIFICATION SET timestamp=? WHERE email=(?)",t)
    updateVerificationCount(email,1)
    g.db.commit()


def emailExists(email):
    t = (email,)
    result = query_db('SELECT COUNT(email) FROM USERS WHERE email=(?)', t, one=True)
    count = result[0]
    if count > 0:
        return True
    return False

def makeEmailActive(email):
    g.db = get_db()
    t = (email,)
    g.db.execute('UPDATE USERS SET isVerified=1 WHERE email=?',t)
    g.db.commit()

#return true if success. else return false
def sendVerificationEmail(email):
    notificationEmail = app.config['NOTIFICATIONEMAIL']
    emailPw = app.config['EMAILPW']
    token = getToken(email)
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    try:
        server.login(notificationEmail, emailPw)
    except smtplib.SMTPAuthenticationError as e:
        runSMTPAuthExceptionCode(server, e)

    msg = MIMEText("Click the link to confirm your e-mail \n\n" + "http://" + app.config['HOST'] + ":" + str(app.config['PORT'])+ \
                   "/verifyEmail?token="+token)

    msg['To'] = email
    msg['From'] =notificationEmail
    msg['Subject'] = 'email verification'
    try:
        server.sendmail(notificationEmail, email, msg.as_string())
        return True
    except:
        return abort(500)
    finally:
        server.quit()
#return false if email failed to send
def sendForgotPassword( email):
    dbToken = getToken(email)
    url = "http://" + app.config['HOST'] + ":" + str(app.config['PORT']) + "/processResetPassword?email=" + email + "&token=" + dbToken
    htmlMsg = """
    <html>
    <header></header>
    <body>
    <p>Hello from freeChamp! Click <a href=""" + url + ">here</a> to reset your password</body></html>"



    plainMsg = "Hello from freeChamp! Click the following link to reset your password: " + url


    subject = "freeChamp password reset"
    emailSent = sendEmail(email, subject, plainMsg, htmlMsg)
    if not emailSent:
        return False
    else:
        return True

def sendEmail(toEmail, subject, body, html):
    notificationEmail = app.config['NOTIFICATIONEMAIL']
    emailPw = app.config['EMAILPW']
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    try:
        server.login(notificationEmail, emailPw)
    except smtplib.SMTPAuthenticationError as e:
        runSMTPAuthExceptionCode(server, e)
        return False

    msg = MIMEMultipart('alternative')
    # Create the body of the message (a plain-text and an HTML version).
    text = body
    msg['To'] = toEmail
    msg['From'] = notificationEmail
    msg['Subject'] = subject
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    email_text =  msg.as_string()
    try:
        server.sendmail(notificationEmail, toEmail, email_text)
        return True
    finally:
        server.quit()

def sendChampNotifEmail(apiIds):
    logging.basicConfig(filename='freeChampEvents.log',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
level=logging.INFO)
    subject = "Free Champion Notification"
    g.db = get_db()
    #reset free bool
    g.db.execute("UPDATE CHAMPS SET free = 0")
    #for each champ id in the api call, show that champ as free in the db
    for champId in apiIds:
         g.db.execute("UPDATE Champs SET free = 1 WHERE id = (?)", (champId,))
    g.db.commit()
    #get a list of users that have selected champs they want to be notified when they are free
    emails = [email[0] for email in query_db("SELECT Distinct Notify.Email FROM Notify JOIN Champs ON Champs.Champ = Notify.Champ WHERE Champs.Free = 1")]
    emailNum = len(emails)
    logging.info("sending " + str(emailNum) + " notification email(s)")
    print("updating free champ rotation. \n" + str(len(emails)) + " emails in this update")
    for email in emails:
        freeChampsSelectedByUser = [champ[0] for champ in query_db("""
            SELECT champs.champ
            FROM CHAMPS
            JOIN notify ON champs.champ = notify.champ
            where notify.email=(?) and champs.free = 1 order by champs.champ""", (email,))]

        msg = "Hello from Free Champ! You wished to be notified when the below champs are free: \n"

        for champ in freeChampsSelectedByUser:
            msg += champ + '\n'
        token = getToken(email)
       #msg += "\n\n <a href=http://" + app.config['HOST'] + ":" + str(app.config['PORT']) + "/optOut>opt-out?token=" + token + "</a>"
        msg += getOptOutMessage(token)
        htmlMsg = """
        <html>
        <header></header>
        <body>
        <p>Hello from Free Champ! You wished to be notified when the below champs are free:<br/><br/>"""
        for champ in freeChampsSelectedByUser:
            htmlMsg += champ + "<br/>"
        htmlMsg += getOptOutMessage(token, isHTML=True)
        htmlMsg += "</body></html>"
        sendEmail(email, subject, msg, htmlMsg)

def resetVerificationCount(email):
    g.db = get_db()
    t = (email,)
    g.db.execute('UPDATE verification SET count=0 WHERE email=?',t)
    g.db.commit()

def updateVerificationCount(email, count):
    t = (count, email)
    g.db = get_db()
    g.db.execute('UPDATE verification SET count=? WHERE email=?',t)
    g.db.commit()

def getCount( email):
    t = (email,)
    (count,) = query_db('SELECT count FROM verification WHERE email=?',t,one=True)
    return count

def verificationFromToday(email):
     g.db = get_db()
     t = (email,)
     result = query_db("SELECT count(strftime('%Y-%m-%d',timestamp,'localtime')) from verification WHERE strftime(" + \
                      "'%Y-%m-%d',timestamp,'localtime')=strftime('%Y-%m-%d','now','localtime') and email=?",t,one=True)
     count = result[0]
     return count == 1


 #returns true if send limit has not been exceeded for a given email
def checkSendLimit(email):
    if emailExists(email):
        count = getCount(email)
        if count == 0:
            updateVerificationCount(email,1)
            return True
        elif count == 1:
            updateVerificationCount(email,2)
            return True
        else:
            token = getToken(email)
            if not tokenIsAlive(token):
                refreshVerification(email)
                return True
            return False
    else:
        return False

def runSMTPAuthExceptionCode(server, e):
    logging.basicConfig(filename='freeChampError.log',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.ERROR)
    logging.error("smtp error" + str(e.smtp_code) + ": " + e.smtp_error)
    server.quit()