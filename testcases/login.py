# -*- coding: utf-8 -*-
import sys
sys.path.append("app/main/defender/main")
from android.basecase import AndroidDevice


class TestCase(AndroidDevice):
    desc = "登录后验证个人信息中的手机号是否跟登录账号一致,并检查个人信息页UI"

    def __init__(self,ce,dc):
        self.dc = dc
        print(dc)
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

        self.super_click("登录按钮")

        username,password = self.conflictdatas("登录账号")

        self.super_input("登录手机号输入框",username)

        self.super_input("登录密码输入框",password)

        self.super_click("登录按钮")

        self.back()

        self.super_click("功能导航按钮")

        self.super_click("功能导航-头像")

        phone_num = self.super_gettext("个人信息-手机号")

        self.log("手机号：%s  个人信息-手机号：%s" %(username,phone_num))

        assert phone_num == username,"登录账号与个人信息中手机号不一致"

        infos = ["个人资料","用户信息","头像","用户名","手机号","基本资料","学校","专业","入学年份","楼栋","寝室号","保存"]

        self.exist_texts(infos)
