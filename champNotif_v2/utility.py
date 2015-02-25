__author__ = 'Paul'
import os, hashlib

def genRandomString(self):
    randomBytes = os.urandom(32)
    hash = hashlib.sha512()
    hash.update(randomBytes)
    return hash.hexdigest()