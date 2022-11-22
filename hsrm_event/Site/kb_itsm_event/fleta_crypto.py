#!/usr/bin/env python
#-*- coding: utf-8 -*-

import base64
import pyDes


def iv(pad=chr(0)):
    return pad * 8


class AESCipher(object):
    def __init__(self, key='kes2719!'):
        self.key = key

    def encrypt(self, message):
        k = pyDes.des(self.key, pyDes.ECB, iv(), pad=None, padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(message)
        return base64.b64encode(d)

    def decrypt(self, enc):
        k = pyDes.des(self.key, pyDes.ECB, iv(), pad=None, padmode=pyDes.PAD_PKCS5)
        data = base64.b64decode(enc)
        d = k.decrypt(data)
        return d


if __name__ == '__main__':
    fc = AESCipher('kes2719!')
    # print(crypt_me)
    pw=input('enter passwd :')
    e=fc.encrypt(pw)
    # e="MfmNWa/dtZt6SN+m0rbfpg=="

    t = fc.decrypt(e)
    print(t)
    print(e)
    if isinstance(e,bytes):
        ps_str = e.decode('utf-8')
        print('패스위드 암호화 : {}'.format(ps_str))

