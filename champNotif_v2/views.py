__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort,flash
from Email import *
from champToken import *
from security import securePw
from utility import genRandomString

emailLib = Email()
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    error = None

    postEmail = request.form['varEmail']
    postPw = request.form['varPassword']
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
                return redirect('member_pg')
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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

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


