__author__ = 'Paul'

from champNotif_v2 import app
from flask import session, redirect, url_for, render_template, request
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
        pw = request.form['varPassword']
        salt = emailLib.genRandomString()
        isVerified = 0 #false
        emailLib.addEmail(email, pw, salt, isVerified)
        canSend = emailLib.checkSendLimit(email)
        if canSend:
            return 1



        else:
            t = (email, pw, salt, isVerified)
            #check if the email already exists
            exists = emailLib.emailExists(email)

            #if the email does not exist, send the verification email
            #result = query_db('select * from USERS where email=?',t,one=True)
    return email

@app.route('/verifyEmail')
def verifyEmail():
    email = request.args.get('email')
    canSend = emailLib.checkSendLimit(email)
    if canSend:
        token =
        emailLib.sendVerificationEmail(email,token)