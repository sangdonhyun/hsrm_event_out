#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pyDes
import base64
import chardet

def iv():
    return chr(0) * 8

class AESCipher(object):
    def __init__(self, key):
        self.key = key
        self.iv = iv()

    def encrypt(self, message):
        k = pyDes.des(self.key, pyDes.ECB, self.iv, pad=None, padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(message)
        d = base64.b64encode(d)
        d = self.check_bytes(d)
        return d

    def decrypt(self, enc):
        k = pyDes.des(self.key, pyDes.ECB, self.iv, pad=None, padmode=pyDes.PAD_PKCS5)
        data = base64.b64decode(enc)
        d = k.decrypt(data)
        d = self.check_bytes(d)
        return d

    def check_bytes(self, s_data):
        s_result = ''
        if isinstance(s_data, bytes):
            try:
                s_result = s_data.decode()
            except:
                s_enc_data = chardet.detect(s_data)['encoding']
                try:
                    s_result = s_data.decode(s_enc_data)
                except:
                    return s_data
        else:
            s_result = s_data
            
        return s_result