__author__ = 'S70rmCrow'
import hashlib, binascii
from os import sys


def securePw(salt, pw):
    dk = hashlib.pbkdf2_hmac('sha512', pw, salt, 100000)
    return binascii.hexlify(dk)
