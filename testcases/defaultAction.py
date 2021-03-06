# -*- coding: utf-8 -*-
import sys
sys.path.append("app/main/defender/main")
from android.basecase import AndroidDevice


class TestCase(AndroidDevice):
    desc = "登录用例"

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

        self.allow_alert(nocheck=True)

        self.allow_alert(nocheck=True)

        username,password = self.conflictdatas("登录账号")

        self.log("username:%s password:%s" %(username,password))

        self.click("登录按钮")

        self.input("手机号输入框",username)

        self.input("密码输入框",password)

        self.click("登录按钮")

        self.reject_alert()
