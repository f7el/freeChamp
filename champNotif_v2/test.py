from champNotif_v2 import app
from .database import query_db
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


t = (2, 3)
query_db('UPDATE test SET name=paul WHERE id IN ?', t)

