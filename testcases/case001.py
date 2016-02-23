# -*- coding: utf-8 -*-
import sys
sys.path.append("C:/Users/Administrator/Desktop/selftest/testplatform/app/main/defender/main")
from android.basecase import AndroidDevice
from time import sleep;import requests;

class TestCase(AndroidDevice):
    desc = "测试"

    def __init__(self,ce,dc):
        self.dc = dc
        self.appium_port = ce['port']
        self.bootstrap_port = ce['bootstrap_port']
        self.device_name = dc['deviceName']
        self.appium_url = ce['url']
        self.filename = str(self.__class__).split('.')[0].split("'")[1]
        self.casename = '%s_%s_%s' %(dc['deviceName'].replace('.','_').replace(":","_"),ce['port'],self.filename)

    def __call__(self,conflict_datas):
        super(TestCase,self).__init__(conflict_datas,command_executor=self.appium_url,desired_capabilities=self.dc)
        return self

    def __repr__(self):
        return "<Testcase:%s>" %self.filename

    def run(self):
        self.implicitly_wait(10)

        data = self.testdatas("测试")

        self.log(data)

        username,password = self.conflictdatas("登录账号")

        self.log("username:%s password:%s" %(username,password))

        self.super_click("注册登录按钮")
