__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort, flash
from champNotif_v2 import Email
from champNotif_v2.champToken import *
from .security import securePw
from .utility import genRandomString
from .riotApi import *
from .validate import *
import logging
from champNotif_v2 import gResponse
from .forgotPassword import *
import os

app.secret_key = bytearray(str(os.urandom(16)), 'utf-8')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    postEmail = request.form['varEmail']
    postPw = request.form['varPassword']
    if emailIsValid(postEmail):
        if passwordIsValid(postPw):
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
        else:
            abort(400)
    else:
        abort(400)


@app.route('/members')
def members():
    if 'logged_in' in session:
        (dragonVer,) = query_db("SELECT version from dragonVer", one=True)
        t = session['email']
        lstChamps = query_db("""SELECT champs.champ, champs.key, champs.id, champs.free,
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
        if emailIsValid(email):
            pw = request.form['varPassword']
            if passwordIsValid(pw):
                salt = genRandomString()
                newPw = securePw(salt, pw)
                isVerified = 0 #false
                newPlayer = request.form['varNewPlayer']
                Email.addEmail(email, newPw, salt, isVerified, newPlayer)
                token = genRandomString()
                Email.addVerification(email,token)
                result = Email.sendVerificationEmail(email)
                if result == True:
                    return 'OK'
                else:
                    abort(500)
            else:
                abort(400)
        else:
            abort(400)

    #NEED TO MAKE CUSTOM HANDLER FOR EMAIL ALREADY EXISTS <---------------------------------------------
    else:
        abort(401)

@app.route('/sendAnotherVerification', methods=['GET'])
def sendAnotherVerification():
    if request.method == 'GET':
        email = request.args['varEmail']
        if Email.emailExists(email):
            if emailIsValid(email):
                canSend = Email.checkSendLimit(email)
                if canSend:
                    if Email.sendVerificationEmail(email):
                        return "OK"
                #user has surpassed their registration limit
                else:
                    return "user has surpassed the send limit"
            else:
                abort(400)
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
    jObj = getFreeChampRotations()
    newPlayerChampRotation = jObj['freeChampionIdsForNewPlayers']
    champRotation = jObj['freeChampionIds']
    champDicts = getDataDict()
    for champ in champDicts:
        champDict = champDicts[champ]
        name = champDict['name']
        key = champDict['key']
        id = champDict['id']
        free = 0
        freeNew = 0
        if (int(key) in newPlayerChampRotation):
            freeNew = 1
        if (int(key) in champRotation):
            free = 1
        t = (name,key, id, free, freeNew)
       

            
        g.db.execute("INSERT INTO CHAMPS (champ, key, id, free, freeNew) VALUES (?, ?, ?, ?, ?)", t)
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
            key = champData['key']
            #freeData = getChampInfoById(key)
            if freeData['freeToPlay'] == False:
                isFree = 0
            else:
                isFree = 1

            t = (name, key, isFree)
            g.db.execute("INSERT INTO CHAMPS VALUES (?, ?, ?)", t)
        g.db.commit()
        return "True"
    return "False"

@app.route('/champUnselected', methods=['POST'])
def champUnselected():
    if 'logged_in' in session:
        email = session['email']
        champName = request.form['varChampName']
        if champName == "ALL":
            t = (email,)
            g.db = get_db()
            g.db.execute("DELETE FROM NOTIFY WHERE email=(?)", t)
            g.db.commit()
            return 'OK'
        elif nameIsValidated(champName):
            t = (email, champName)
            g.db = get_db()
            g.db.execute("DELETE FROM NOTIFY WHERE email=(?) and champ=(?)", t)
            g.db.commit()
            return 'OK'
        else:
            abort(400)
    abort(401)

""" @app.route('updateNewPlayer', methods['POST'])
def updateNewPlayer():
    if 'logged_in' in session: """


@app.route('/champSelected', methods=['POST'])
def champSelected():
    if 'logged_in' in session:
        champName = request.form['varChampName']
        if champName == "ALL":
            g.db = get_db()
            t = (session['email'],session['email'])
            g.db.execute("""INSERT INTO Notify (champ, email)
                            SELECT Champs.champ, (?)
                            FROM Champs
                            LEFT JOIN Notify ON Champs.champ = Notify.champ AND Notify.email =(?)
                            WHERE Notify.champ IS NULL""", t)
            g.db.commit()
            return "OK"
        elif nameIsValidated(champName):
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
    print (lstChamps[0]['champ'] + lstChamps[0]['key'] + lstChamps[0]['Selected'])

@app.route('/freeChampPollTest')
def freeChampPollTest():
    subject = "Free Champion Notification"
    emails = [email[0] for email in query_db("SELECT Distinct Notify.Email FROM Notify JOIN Champs ON Champs.Champ = Notify.Champ WHERE Champs.Free = 1")]
    print (emails)
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
    dbFreeChampKeys = [key[0] for key in query_db("SELECT key from CHAMPS WHERE free=1")]
    dbNewFreeChampKeys = [key[0] for key in query_db("SELECT key from CHAMPS WHERE freeNew=1")]
    jObj = getFreeChampRotations()
    newPlayerChampRotation = jObj['freeChampionIdsForNewPlayers']
    champRotation = jObj['freeChampionIds']
    champKeys = [key[0] for key in query_db("SELECT key from CHAMPS")]
    diff = list(set(dbFreeChampKeys) - set(champRotation))
    if len(diff) > 0:
        g.db = get_db()
        g.db.execute('UPDATE champs SET free=0')
        g.db.commit() 
        for id in champRotation: 
            db = get_db()
            db.execute("UPDATE champs SET free=1 WHERE key=(?)", (id,))   
            db.commit()
        #Email.sendChampNotifEmail(apiIds)
    diff = list(set(dbNewFreeChampKeys) - set(newPlayerChampRotation))
    if len(diff) > 0:
        g.db = get_db()
        g.db.execute('UPDATE champs SET freeNew=0')
        g.db.commit()
        for id in newPlayerChampRotation:
            db = get_db()
            db.execute("UPDATE champs SET freeNew=1 WHERE key=(?)", (id,))   
            db.commit()
    return "OK"

@app.route('/optOut', methods=['GET'])
#gets token from url. if the token is valid, allow the user to opt-out
def optOut():
    token = request.args['token']
    if tokenExists(token):
        session['email'] = getEmailFromToken(token)
        return render_template('optOut.html')
    else:
        abort(401)

#removes all notify entries for a given email
@app.route('/processOptout', methods=['GET'])
def processOptout():
    #if the user is not logged in, direct to login page
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
            #check if an entry exists in reset table
            if not resetAttemptExists(email):
                insertResetAttempt(email)
                emailSent = Email.sendForgotPassword(email)
            #if an entry exists, check if it has exceeded 24-hrs
            elif canResetPw(email):
                refreshPwTimestamp(email)
                emailSent = Email.sendForgotPassword(email)
            #exceeded 24-hr limit
            else:
                abort(403)

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

@app.route('/about')
def about():
    return render_template('about.html')

