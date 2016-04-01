# -*- coding: utf-8 -*-
import sys
sys.path.append("app/main/defender/main")
from android.basecase import AndroidDevice
import random;

class TestCase(AndroidDevice):
    desc = "修改个人资料后验证是否修改成功"

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

        nicknames = [self.testdatas("十二位数字"),self.testdatas("十二位字母"),self.testdatas("十二位中文"),self.testdatas("十二位特殊字符")]

        for index,name in enumerate(nicknames):

            self.super_click("功能导航-头像")

            self.super_click("个人信息-用户名")

            self.super_input("个人信息-修改-输入框",name)

            self.super_click("个人信息-修改-返回")

            self.exist_text(name)

            if index%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.exist_text(name)

        schools = ["安徽","上海","北京","理工","科技","随米"]

        for index,school in enumerate(schools):

            self.super_click("功能导航-头像")

            self.super_click("个人信息-学校")

            self.super_input("个人信息-修改-输入框",school)

            lists = self.super_finds("个人信息-修改-列表")

            elem = lists[random.randint(0,len(lists)-1)]

            name = str(elem.text)

            elem.click()

            self.super_click("个人信息-修改-返回")

            if school == "随米":

                name = "测试学校"

            else:

                self.exist_text(name)

            if index%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.exist_text(name)

        self.super_click("功能导航-头像")

        majors = ["计算机","科学","数学","金融"]

        for index,major in enumerate(majors):

            self.super_click("个人信息-专业")

            self.super_input("个人信息-修改-输入框",major)

            lists = self.super_finds("个人信息-修改-列表")

            elem = lists[random.randint(0,len(lists)-1)]

            name = str(elem.text)

            elem.click()

            self.super_click("个人信息-修改-返回")    

            self.exist_text(name)

            if index%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.super_click("功能导航-头像")

            self.exist_text(name)

        for i in range(3):

            self.super_click("个人信息-入学年份")

            lists = self.super_finds("个人信息-修改-列表")

            elem = lists[i]

            name = str(elem.text)

            elem.click()

            self.super_click("个人信息-修改-返回")    

            self.exist_text(name)

            if i%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.super_click("功能导航-头像")

            self.exist_text(name)

        for i in range(3):

            self.super_click("个人信息-楼栋")

            lists = self.super_finds("个人信息-修改-楼栋列表")

            elem = lists[i]

            name = str(elem.text)

            elem.click()

            self.super_click("个人信息-修改-楼栋返回")    

            self.exist_text(name)

            if i%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.super_click("功能导航-头像")

            self.exist_text(name)

            

        rooms = [self.testdatas("十二位数字"),self.testdatas("十二位字母"),self.testdatas("十二位中文"),self.testdatas("十二位特殊字符")]

        for index,room in enumerate(rooms):

            self.super_click("个人信息-寝室号")

            self.super_input("个人信息-修改-输入框",room)

            self.super_click("个人信息-修改-返回")    

            self.exist_text(room)

            if index%2 == 0:

                self.super_click("个人信息-保存")

                self.super_click("个人信息-返回")

            else:

                self.super_click("个人信息-返回")

                self.super_click("弹框-确认")

            self.super_click("功能导航-头像")

            self.exist_text(room)
