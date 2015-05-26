from database import query_db
def nameIsValidated(name):
    t = (name,)
    count = [count[0] for count in query_db("select count(champ) from champs where champ=(?)", t)]
    return count[0] == 1