__author__ = 'S70rmCrow'
import os, hashlib

def securePw(self, salt, pw):
    hash = hashlib.sha512()
    hash.update(salt + pw)
    return hash.hexdigest()