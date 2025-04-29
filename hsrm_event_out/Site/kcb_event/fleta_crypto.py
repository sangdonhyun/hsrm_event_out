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

    def test(self):
        fc = AESCipher()
        pw='qc19721108*'
        e = fc.encrypt(pw)
        t = fc.decrypt(e)
        print(e)
        # print(type(e))
        print(t)
        # print(type(t))
        if isinstance(e,bytes):
            print(type(e.decode('utf-8')))

if __name__ == '__main__':
    AESCipher().test()
    fc = AESCipher()
    # print(crypt_me)
    pw=input('enter passwd :')
    e=fc.encrypt(pw)
    # e="MfmNWa/dtZt6SN+m0rbfpg=="

    t = fc.decrypt(e)
    print('t :',t)
    print('e :',e)
    if isinstance(e,bytes):
        ps_str = e.decode('utf-8')
        print('패스위드 암호화 : {}'.format(ps_str))
    #
    # pw="KTogOT8Yy/LWtMJ7YtmQug=="
    # print(str(fc.decrypt(ps_str)))
