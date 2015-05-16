__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort, flash
from Email import *
from champToken import *
from security import securePw
from utility import genRandomString
from riotApi import getDataDict


emailLib = Email()
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    error = None

    #postEmail = request.form['varEmail']
    #postPw = request.form['varPassword']
    postEmail = request.form['email']
    postPw = request.form['pw']
    t = (postEmail,)
    if emailLib.emailExists(postEmail):
        result = query_db('SELECT * FROM users WHERE email=?', t)
        resultList = result[0]
        email, hashedPw, salt, isVerified = resultList

        if isVerified == 1:
            isVerified = True
        else:
            isVerified = False

        print "isVerified: " + str(isVerified)
        if isVerified:
            loginPw = securePw(salt, postPw)

            if loginPw == hashedPw:
                session['logged_in'] = True
                session['email'] = postEmail
                return redirect(url_for('members'))
            else:
                abort(401)
        else:
            abort(401)

        if request.form['email'] != None: #FIX ME LATER
            error = 'invalid login'
        elif request.form['password'] != None: #FIX ME LATER
            error = 'invalid login'
        else:
            session['logged_in'] = True
            return redirect(url_for('member_page')) #FIX ME LATER
    return render_template('login.html', error=error)

@app.route('/members')
def members():
    if 'logged_in' in session:
        champ = [champ[0] for champ in query_db("select champ from champs")]
        key = [key[0] for key in query_db("select key from champs")]
        dictChamps = dict(zip(champ,key))
        return render_template('members.html', dictChamps=dictChamps, postEmail=session['email'])
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
    if request.method == 'POST':
        email = request.form['varEmail']
        if not emailLib.emailExists(email):
            pw = request.form['varPassword']
            salt = genRandomString()
            #hash(salt + pw)
            newPw = securePw(salt,pw)
            isVerified = 0 #false
            emailLib.addEmail(email, newPw, salt, isVerified)
            token = genRandomString()
            emailLib.addVerification(email,token)
            emailLib.sendVerificationEmail(email,token)
            return 'OK'


        #NEED TO MAKE CUSTOM HANDLER FOR EMAIL ALREADY EXISTS <---------------------------------------------
        else:
            abort(400)

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
        t = (name,key)
        g.db.execute("INSERT INTO CHAMPS VALUES (?,?)", t)
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
    apiNames.append("Kyle")
    apiNames.append("Paul")
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
        email = request.form['varUser']
        champName = request.form['varChampName']
        t = (email, champName)
        g.db = get_db()
        g.db.execute("DELETE FROM NOTIFY WHERE email=(?) and champ=(?)", t)
        g.db.commit()
        return 'OK'
    abort(401)


@app.route('/champSelected', methods=['POST'])
def champSelected():
    if 'logged_in' in session:
        email = request.form['varUser']
        champName = request.form['varChampName']
        t = (champName, email)
        g.db = get_db()
        g.db.execute("INSERT INTO NOTIFY VALUES (?,?)", t)
        g.db.commit()
        return 'OK'
    abort(401)

@app.route('/unauthorized', methods=['GET'])
def unauthorized():
    return render_template('401.html')

@app.route('/logged_in', methods=['POST'])
def logged_in():
    if 'logged_in' in session:
        return 'OK'
    abort(401)