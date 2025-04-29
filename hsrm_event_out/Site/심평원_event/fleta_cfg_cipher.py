
import os
import sys
import getpass
import traceback
import configparser

from inspect import currentframe, getframeinfo

import common
import aescipher


class PasswdEncrytor():
    def __init__(self):
        self.o_common = common.Common()
        self.o_aes = aescipher.AESCipher(key='kes2719!')

    def main_menu(self):
        print('Target dir?)')
        print('1) list')
        print('2) config')
        print('3) exit')
        s_select=input('1/2>')
        return s_select.strip()

    def sub_menu(self):
        print('Sub)')
        print('  1) Encoding')
        print('  2) Decoding')
        s_select=input('1/2>')
        return s_select.strip()

    def choose_type(self):
        print('Choose File)')
        print('  )ALL')
        print('  )Type Name : EX)PURE, ISILON')
        s_select = input('>')
        return s_select

    def get_list_dir_file_path(self, a_vendor_list):
        a_work_file = []
        s_file_type = 'list.cfg'
        # list dir 에 있는 모든 파일중 s_file_type에 맞는 모든 파일
        if a_vendor_list.strip().upper() == 'ALL':
            a_file_name = os.listdir('list')
            for s_file_name in a_file_name:
                if s_file_type in s_file_name:
                    s_file_path = os.path.join('list', s_file_name)
                    a_work_file.append(s_file_path)
        # list dir 에 있는 파일중 s_file_type에 맞는 선택 파일
        else:
            a_device_type = a_vendor_list.split(',')
            for s_device_type in a_device_type:
                s_file_name = s_device_type.strip() + s_file_type
                s_file_path = os.path.join('list', s_file_name)
                a_work_file.append(s_file_path)

        if len(a_work_file) < 1:
            print('Please check encrypt target-file')
            sys.exit()
        
        return a_work_file

    def list_file_encrpyt(self, a_target_file_list, s_type):
        a_succ_file = []
        for s_target_file in a_target_file_list:
            b_success = self.enc_working(s_target_file, s_type)
            if b_success:
                a_succ_file.append(s_target_file)
                print(s_target_file + ': SUCCESS')
            else:
                print(s_target_file + ': FAIL')

        s_content = str(a_succ_file) + ' is ' + s_type + 'rypt!!'
        print(s_content)
        print('Finish')

    def get_cfg(self, s_file_path):
        if not os.path.isfile(s_file_path):
            print('Please Check %s'%(s_file_path))
            sys.exit()

        o_cfg = configparser.RawConfigParser()
        o_cfg.read(s_file_path)
        return o_cfg
    
    def get_file_list(self, s_dir):
        print('s_dir : ',s_dir)
        a_target_file_list = []
        a_file_list = os.listdir(s_dir)
        print('a_file_list ',a_file_list)
        for s_file in a_file_list:
            if 'config.cfg' in s_file.lower():
                s_file_path = os.path.join(s_dir, s_file)
                a_target_file_list.append(s_file_path)

        return a_target_file_list

    def enc_working(self, s_file_path, s_type):
        try:
            o_cfg = self.get_cfg(s_file_path)
            for s_sec in o_cfg.sections():
                for s_opt in o_cfg.options(s_sec):
                    if s_opt.upper() in ['PASSWD','PASSWORD','CLIPASSWD','SVP_PASSWORD']:
                        s_pw = o_cfg.get(s_sec,s_opt)
                        try:
                            if s_type == 'enc':
                                try:
                                    self.o_aes.decrypt(s_pw)
                                except:
                                    s_pw = self.o_aes.encrypt(s_pw)
                            elif s_type == 'dec':
                                s_pw = self.o_aes.decrypt(s_pw)
                        except:
                            pass

                        o_cfg.set(s_sec,s_opt,s_pw)
            with open(s_file_path, 'w') as s_content:
                o_cfg.write(s_content)
            return True
        except Exception as e:
            cFrameinfo = getframeinfo(currentframe())
            cTraceback = traceback.TracebackException.from_exception(e)
            s_except = ''.join(cTraceback.stack.format()) + str(e)
            print(cFrameinfo.filename, s_except)
            return False

    def main(self):
        print(self.o_common.getHeadMsg('fleta config decoding'))
        while True:
            s_main_sel = self.main_menu()

            if s_main_sel.strip() not in ['1','2','3']:
                print('Please enter 1 or 2 or 3.')
                continue

            # ssh password encrypt
            print(s_main_sel.strip())
            if s_main_sel.strip() == '1':
                print('list directory')
                # if not os.path.isdir('list'):
                #     print('Please Check list directory')
                #     sys.exit()

                s_select_type = self.choose_type()
                print(s_select_type)
                a_target_file_list = self.get_list_dir_file_path(s_select_type)
                print('a_target_file_list :',a_target_file_list)
                while True:
                    s_sub_sel=self.sub_menu()
                    if s_sub_sel == '1':
                        self.list_file_encrpyt(a_target_file_list, s_type='enc')
                        break

                    elif s_sub_sel == '2':
                        self.list_file_encrpyt(a_target_file_list, s_type='dec')
                        break
                    else:
                        continue
                break

            elif s_main_sel.strip() == '2':
                print('config directory')
                a_file_path_list = self.get_file_list('config')
                print(a_file_path_list)
                while True:
                    s_sub_sel=self.sub_menu()
                    if s_sub_sel == '1':
                        self.list_file_encrpyt(a_file_path_list, s_type='enc')
                        break
                    elif s_sub_sel == '2':
                        self.list_file_encrpyt(a_file_path_list, s_type='dec')
                        break
                    else:
                        continue
                
            print(self.o_common.getEndMsg())
            sys.exit()


if __name__=='__main__':
    PasswdEncrytor().main()
    # cnt=0
    # print('fleta password encoder')
    # s_pwd = getpass.getpass('password :')
    # print(s_pwd)
    # while True:
    #     s_pwd=getpass.getpass()
    #     if s_pwd.strip() != 'fleta123':
    #         cnt = cnt+1
    #         print('password incorrect')
    #     else:
    #         PasswdEncrytor().main()
    #
    #     if cnt==3:
    #         print('bye')
    #         break
    #