# -*- coding: utf-8 -*-
import sys
sys.path.append("app/main/defender/main")
from android.basecase import AndroidDevice


class TestCase(AndroidDevice):
    desc = "测试文库-更多的文档预览和过程中的页面检查"

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

        self.super_input("手机号输入框",username)

        self.super_input("密码输入框",password)

        self.super_click("登录按钮")

        self.back()

        self.super_click("功能导航按钮")

        self.super_click("功能导航-文库")

        check_texts = ["文库","热点","通用课程","高数","马哲","思修","更多 >"]

        self.exist_texts(check_texts)

        self.super_click("文库-更多")

        articles = self.super_finds("文库-更多-文档名列表")

        assert len(articles)>0,"列表中未找到文档信息"

        for article in articles:

            title1 = article.text

            article.click()

            check_texts = ["添加到打印","评论","收藏文档"]

            self.exist_texts(check_texts)

            title2 = self.super_find("文档详情页-标题").text

            self.equals(title1,title2)

            self.super_click("文档详情页-返回")
