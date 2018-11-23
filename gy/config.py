#!/usr/bin/env python
import json,sys,os

class GyConfig:
    def __init__(self):
        PROJ_PATH= "E:/OnionMall/"
        if "PROJ_PATH" in os.environ:
            PROJ_PATH = os.environ['PROJ_PATH']
        file_name = "config.win"
        if "CONF_FILE" in os.environ:
            file_name = os.environ['CONF_FILE']
        config_file='%sgy/%s' % (PROJ_PATH, file_name)
        self.proj_path=PROJ_PATH
        self.user_info = {"username": "13119182428", "password": "lcl12345"}
        with open(config_file) as fp:
            self.config = json.load(fp)

    def get_chrome_executable_path(self):
        return self.config.get('chrome_execute_path')

    def get_os_type(self):
        return self.config.get('os_type')

    def get_http_proxy(self):
        return self.config.get('http_proxy')

    def get_chrome_user_dir(self):
        return self.get_chrome_user_dir_by_user_info(self.user_info)

    def get_chrome_user_root_dir(self):
        return self.config.get('chrome_user_root_dir')

    def get_chrome_user_dir_by_user_info(self, user_info):
        pattern = '%s/%s'
        if self.config.get('chrome_user_dir').endswith('/'):
            pattern = '%s%s'
        return pattern % (self.config.get('chrome_user_dir'), user_info['username'])

    def get_chrome_user_dir_by_key(self, key):
        return self.config.get(key)

    def is_headless(self):
        return self.config.get('is_headless')

    def get_screen_path(self):
        return '%sscreen/' % self.proj_path

    def get_user_info_path(self):
        return '%sdata/' % self.proj_path

    def get_user_info(self):
        file_name = ''
        if len(sys.argv) > 1:
            file_name = sys.argv[1]
        return self.get_user_info_by_file_name(file_name)

    def get_user_info_by_file_name(self, file_name):
        user_file_name = '%s%s' % (self.get_user_info_path(), file_name)
        print('File to load user info:', user_file_name)
        try:
            with open(user_file_name) as fp:
                self.user_info = json.load(fp)
        except:
            print('Unable to load user info, we use default info')
            return {'username':'13632265913', 'password': 'lcl1229'}
        return self.user_info
