__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort, flash
from Email import *
from champToken import *
from security import securePw
from utility import genRandomString
from riotApi import getDataDict, getListOfChampDicts
from validate import nameIsValidated

emailLib = Email()
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    postEmail = request.form['email']
    postPw = request.form['pw']
    t = (postEmail,)
    if emailLib.emailExists(postEmail):
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

@app.route('/members')
def members():
    if 'logged_in' in session:
        t = session['email']
        lstChamps = query_db("""SELECT champs.champ, champs.key, champs.free,
                                    case when notify.email is not null
                                        then 'true'
                                        else 'false'
                                    end Selected
                                FROM champs
                                LEFT JOIN notify ON champs.champ = notify.champ AND notify.email = (?)
                                ORDER BY champs.champ;""", (t,))


        return render_template('members.html', lstChamps=lstChamps, postEmail=session['email'])
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
    if not emailLib.emailExists(email):
        pw = request.form['varPassword']
        salt = genRandomString()
        newPw = securePw(salt,pw)
        isVerified = 0 #false
        emailLib.addEmail(email, newPw, salt, isVerified)
        token = genRandomString()
        emailLib.addVerification(email,token)
        emailLib.sendVerificationEmail(email,token)
        return 'OK'

    #NEED TO MAKE CUSTOM HANDLER FOR EMAIL ALREADY EXISTS <---------------------------------------------
    else:
        abort(401)

@app.route('/sendAnotherVerification', methods=['GET'])
def sendAnotherVerification():
    if request.method == 'GET':
        email = request.args['email']
        if emailLib.emailExists(email):
            canSend = emailLib.checkSendLimit(email)
            if canSend:
                token = emailLib.genNewToken(email)
                emailLib.sendVerificationEmail(email,token)

@app.route('/verifyEmail', methods=['GET'])
def verifyEmail():
    #get the request token from the url
    requestToken = request.args['token']

    #check if the token is in the verification data
    exist = tokenExists(requestToken)
    if exist:
        email = getEmailFromToken(requestToken)
        emailLib.makeEmailActive(email)
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

@app.route('/checkForNewChamps', methods=['GET'])
def checkForNewChamps():
    champs = [champ[0] for champ in query_db("select champ from champs")]
    dataDic = getDataDict()

    #get champ keys
    keys = dataDic.keys()
    apiNames = []
    for key in keys:
        champ = dataDic[key]
        apiNames.append(champ['name'])
    #subract the latest champ set from the database set. the difference are new champs
    newChamps = list(set(apiNames) - set(champs))
    #add the new champs to the database
    if len(newChamps) > 0:
        g.db = get_db()
        for champ in newChamps:
            t = (champ,)
            g.db.execute("INSERT INTO CHAMPS VALUES (?)", t)
        g.db.commit()
        flash ("champ db has been updated")
    else:
        flash("champ database up-to-date")
    return render_template('admin.html')

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
            emailLib.sendEmail(email, subject, msg)

    return "OK"
