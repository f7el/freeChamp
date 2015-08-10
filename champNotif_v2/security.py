__author__ = 'S70rmCrow'
import hashlib, binascii

def securePw(salt, pw):
    dk = hashlib.pbkdf2_hmac('sha512', pw, salt, 100000)
    return binascii.hexlify(dk)