__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort, flash
import Email
from champToken import *
from security import securePw
from utility import genRandomString
from riotApi import *
from validate import *
import logging
import gResponse

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    postEmail = request.form['varEmail']
    postPw = request.form['varPassword']
    postGresponse = request.form['varGresponse']

    #check if the captcha was successful
    if gResponse.isVerified(postGresponse):
        t = (postEmail,)
        if Email.emailExists(postEmail):
            result = query_db('SELECT email, password, salt, isVerified FROM users WHERE email=?', t)
            resultList = result[0]
            email, hashedPw, salt, isVerified = resultList

            if isVerified == 1:
                isVerified = True
            else:
                isVerified = False

            if isVerified:
                loginPw = securePw(salt, postPw)

                if loginPw == hashedPw:
                    session['logged_in'] = True
                    session['email'] = postEmail

                    return redirect(url_for('members'))
                else:
                    abort(401)
            else:
                abort(403)
        else:
            abort(401)
    else:
        return 'Invalid captcha', 401

@app.route('/members')
def members():
    if 'logged_in' in session:
        (dragonVer,) = query_db("SELECT version from dragonVer", one=True)
        t = session['email']
        lstChamps = query_db("""SELECT champs.champ, champs.key, champs.free,
                                    case when notify.email is not null
                                        then 'true'
                                        else 'false'
                                    end Selected
                                FROM champs
                                LEFT JOIN notify ON champs.champ = notify.champ AND notify.email = (?)
                                ORDER BY champs.champ;""", (t,))


        return render_template('members.html', lstChamps=lstChamps, postEmail=session['email'], dragonVer=dragonVer)
    else:
        return render_template('401.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/verifyEmailForm')
def verifyEmailForm():
    return render_template('sendVerification.html')

@app.route('/processRegister', methods=['POST'])
def processRegister():
    email = request.form['varEmail']
    if not Email.emailExists(email):
        pw = request.form['varPassword']
        salt = genRandomString()
        newPw = securePw(salt, pw)
        isVerified = 0 #false
        Email.addEmail(email, newPw, salt, isVerified)
        token = genRandomString()
        Email.addVerification(email,token)
        result = Email.sendVerificationEmail(email)
        if result == True:
            return 'OK'
        else:
            abort(500)

    #NEED TO MAKE CUSTOM HANDLER FOR EMAIL ALREADY EXISTS <---------------------------------------------
    else:
        abort(401)

@app.route('/sendAnotherVerification', methods=['GET'])
def sendAnotherVerification():
    if request.method == 'GET':
        email = request.args['varEmail']
        if Email.emailExists(email):
            canSend = Email.checkSendLimit(email)
            if canSend:
                if Email.sendVerificationEmail(email):
                    return "OK"
            #user has surpassed their registration limit
            else:
                return "user has surpassed the send limit"
        #if the email is not in the users table, the user has not performed an initial registration
        else:
            return "use initial verification form"



@app.route('/verifyEmail', methods=['GET'])
def verifyEmail():
    #get the request token from the url
    requestToken = request.args['token']

    #check if the token is in the verification data
    exist = tokenExists(requestToken)
    if exist:
        email = getEmailFromToken(requestToken)
        Email.makeEmailActive(email)
        return render_template('emailActive.html')
    else:
        return render_template('emailVerificationFailed.html')

@app.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html')

@app.route('/insertChamps',methods=['GET'])
def insertChamps():
    g.db = get_db()
    dict = getDataDict()
    keys = dict.keys()
    for key in keys:
        champ = dict[key]
        name = champ['name']
        key = champ['key']
        id = champ['id']
        t = (name,key,int(id))
        g.db.execute("INSERT INTO CHAMPS (champ, key, id) VALUES (?, ?, ?)", t)
    g.db.commit()
    flash("success")
    return render_template('admin.html')

#returns true if new champs were added
@app.route('/checkForNewChamps', methods=['GET'])
def checkForNewChamps():
    logging.basicConfig(filename='freeChampEvents.log',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)
    dbKeys = [champ[0] for champ in query_db("select key from champs")]
    dataDic = getDataDict()

    #get champ keys
    keys = dataDic.keys()
    #apiNames = []
    apiKeys = []
    for key in keys:

        champ = dataDic[key]
        #apiNames.append(champ['name'])
        apiKeys.append(champ['key'])
    #subract the latest champ set from the database set. the difference are new champs
    #newChamps = list(set(apiNames) - set(champs)
    newChampKeys = list(set(apiKeys) - set(dbKeys))
    #add the new champs to the database
    if len(newChampKeys) > 0:
        g.db = get_db()
        for key in newChampKeys:
            #get id of champ
            champData = dataDic[key]
            name = champData['name']
            logging.info('adding %s to the champs db', name)
            id = champData['id']
            freeData = getChampInfoById(id)
            if freeData['freeToPlay'] == False:
                isFree = 0
            else:
                isFree = 1

            t = (name, key, isFree, id)
            g.db.execute("INSERT INTO CHAMPS VALUES (?, ?, ?, ?)", t)
        g.db.commit()
        return "True"
    return "False"

@app.route('/champUnselected', methods=['POST'])
def champUnselected():
    if 'logged_in' in session:
        email = session['email']
        champName = request.form['varChampName']
        if nameIsValidated(champName):
            t = (email, champName)
            g.db = get_db()
            g.db.execute("DELETE FROM NOTIFY WHERE email=(?) and champ=(?)", t)
            g.db.commit()
            return 'OK'
        else:
            abort(400)
    abort(401)

@app.route('/champSelected', methods=['POST'])
def champSelected():
    if 'logged_in' in session:
        champName = request.form['varChampName']
        if nameIsValidated(champName):
            t = (champName, session['email'])
            g.db = get_db()
            g.db.execute("INSERT INTO NOTIFY (champ, email) VALUES (?,?)", t)
            g.db.commit()
            return 'OK'
        else:
           abort(400)
    abort(401)

@app.route('/unauthorized', methods=['GET'])
def unauthorized():
    return render_template('401.html')

@app.route('/logged_in', methods=['POST'])
def logged_in():
    if 'logged_in' in session:
        return 'OK'
    abort(401)

@app.route('/query')
def query():
    lstChamps = query_db("""SELECT champs.champ, champs.key,
                                    case when notify.email is not null
                                        then 'true'
                                        else 'false'
                                    end Selected
                                FROM champs
                                LEFT JOIN notify ON champs.champ = notify.champ AND notify.email = 'vandamere@gmail.com'
                                ORDER BY champs.champ;""")
    print lstChamps[0]['champ'] + lstChamps[0]['key'] + lstChamps[0]['Selected']

@app.route('/freeChampPollTest')
def freeChampPollTest():
    subject = "Free Champion Notification"
    emails = [email[0] for email in query_db("SELECT Distinct Notify.Email FROM Notify JOIN Champs ON Champs.Champ = Notify.Champ WHERE Champs.Free = 1")]
    print emails
    for email in emails:
        freeChampsSelectedByUser = [champ[0] for champ in query_db("""
            SELECT champs.champ
            FROM CHAMPS
            JOIN notify ON champs.champ = notify.champ
            where notify.email=(?) and champs.free = 1 order by champs.champ""", (email,))]

        msg = "Hello from Free Champ! You wished to be notified when the below champs are free: \n"
        htmlChamps = ""
        for champ in freeChampsSelectedByUser:
            msg += champ + '\n'
            htmlChamps += champ + '\n'
        token = getToken(email)
        url = "http://" + app.config['HOST'] + ":" + str(app.config['PORT']) + "/optOut?token=" + token
        msg += "\n\n" + url

        #HTML version
        htmlMsg = """<html>
        <p>Hello from Free Champ! You wished to be notified when the below champs are free: \n</p>""" + htmlChamps \
        +  "<br><br><a href=" + url + ">Opt-Out</a> </html>"




        Email.sendEmail(email, subject, msg, htmlMsg)

    return "OK"

 #determines if a free champ rotation has occured; if so, send an email to the appropriate users
@app.route('/freeChampPoll')
def freeChampPoll():
    champs = getListOfChampDicts()
    dbIds = [id[0] for id in query_db("SELECT id from CHAMPS WHERE free=1")]
    apiIds = []
    for champ in champs:
        if champ['freeToPlay']:
            apiIds.append(champ['id'])
    newFreeChamps = list(set(apiIds) - set(dbIds))

    if len(newFreeChamps) > 0:
        Email.sendChampNotifEmail(apiIds)

    return "OK"

@app.route('/optOut', methods=['GET'])
def optOut():
    return render_template('optOut.html')

#removes all notify entries for a given email
@app.route('/processOptout', methods=['GET'])
def processOptout():
    email = session['email']
    t = (email,)
    g.db = get_db()
    g.db.execute('DELETE FROM notify WHERE email=(?)', t)
    g.db.commit()
    flash("You will no longer receive notifications")
    return render_template('optOut.html')

#update a users password to the specified value
@app.route('/updatePassword', methods=['POST'])
def updatePassword():
    pw = request.form['varPw']

    #if the token in the session equals the token in the database
    if (session['token'] == getToken(session['email'])):
        #if pw is valid, update user's pw in db
        if passwordIsValid(pw):
            salt = getSalt(session['email'])
            hashedPw = securePw(salt, pw)
            g.db = get_db()
            t = (hashedPw, session['email'])
            g.db.execute('UPDATE USERS SET password=(?) WHERE email=(?) ', t)
            g.db.commit()
            return "OK"

    abort(401)

@app.route('/resetPassword', methods=['GET'])
def resetPassword():
    return render_template('resetPassword.html')

@app.route('/sendResetPassword', methods=['GET'])
def sendResetPassword():
    email = request.args['varEmail']
    if emailIsValid(email):
        if Email.emailExists(email):
           emailSent = Email.sendForgotPassword(email)
    if emailSent:
        return 'OK'
    else:
        abort(500)

@app.route('/processResetPassword', methods=['GET'])
def processResetPassword():
    email = request.args['email']
    httpGetToken = request.args['token']
    if emailIsValid(email):
        if Email.emailExists(email):
            dbToken = getToken(email)
            if tokensMatch(httpGetToken, dbToken):
                session['email'] = email
                session['token'] = dbToken
                return render_template('newPassword.html')


#update dragon img repo
@app.route('/updateDragon', methods=['GET'])
def updateDragon():
    logging.basicConfig(filename='freeChampEvents.log',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)
    (dbVer,) = query_db('SELECT version from dragonVer', one=True)
    apiVer = getDragonVer()
    if dbVer == apiVer:
        pass
    else:
        t = (apiVer,)
        g.db.execute('UPDATE dragonVer SET version=(?)', t)
        g.db.commit()
        logging.info('updated dragon version to ' + apiVer)
    return "OK"


