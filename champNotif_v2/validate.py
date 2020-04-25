from .database import query_db
import re
def nameIsValidated(name):
    t = (name,)
    count = [count[0] for count in query_db("select count(champ) from champs where champ=(?)", t)]
    return count[0] == 1

def emailIsValid(email):
    pattern = "^[a-zA-Z0-9+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$"
    return re.match(pattern, email)

def passwordIsValid(pw):
    pattern = "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,8}$"
    return re.match(pattern, pw)