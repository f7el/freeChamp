__author__ = 'Paul'
from .database import get_db, query_db
#log the time a password attempt took place
def insertResetAttempt(email):
    db = get_db()
    (dt,) = query_db("SELECT datetime('now','localtime')", one=True)
    t = (email, dt)

    db.execute("INSERT INTO resetPw (email, timestamp) VALUES (?,?)", t)
    db.commit()

#return true if it has been more than 24-hrs sense last pw reset requet
def canResetPw(email):
    db = get_db()
    t=(email,)
    (dt,) = query_db("SELECT timestamp FROM resetPw WHERE email=?", t, one=True)
    t = (dt,)
    (canSend,) = query_db("SELECT cast((strftime('%s','now','localtime')- strftime('%s',?)) AS real)/60/60 > 24.00",
                            t, one=True)

    return canSend == 1

def refreshPwTimestamp(email):
    db = get_db()
    (dt,) = query_db("SELECT datetime('now','localtime')", one=True)
    t = (dt, email)
    db.execute("UPDATE resetPw SET timestamp=? WHERE email=?", t)
    db.commit()

#return true if an entry exists
def resetAttemptExists(email):
    db = get_db()
    t = (email,)
    (attemptExists,) = query_db("SELECT COUNT (email) FROM resetPw WHERE email=?", t, one=True)
    return attemptExists == 1