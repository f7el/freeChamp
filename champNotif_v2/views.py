__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request, abort,flash
from Email import *
emailLib = Email()
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':

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
            salt = emailLib.genRandomString()
            #hash(salt + pw)
            newPw = emailLib.securePw(salt,pw)
            isVerified = 0 #false
            emailLib.addEmail(email, newPw, salt, isVerified)
            verifyEmail(email)

        #NEED TO MAKE CUSTOM HANDLER FOR EMAIL ALREADY EXISTS <---------------------------------------------
        else:
            abort(400)

@app.route('/verifyEmail')
def verifyEmail(email=None):
    if email == None:
        email = request.args.get('email')
        canSend = emailLib.checkSendLimit(email)
        return render_template('sendVerification.html')


        if canSend:
            token = emailLib.genRandomString()
    #         emailLib.addVerification(email,token)
    #         emailLib.sendVerificationEmail(email,token)
    #         return "email verification sent"
    #     else:
    #         return False
    # else:
    #     canSend = emailLib.checkSendLimit(email)
    #     if canSend:
    #         token = emailLib.genRandomString()
    #         emailLib.addVerification(email,token)
    #         emailLib.sendVerificationEmail(email,token)
    #         return "email verification sent"
    #     else:
    #         abort(404)
