# -*- coding: utf-8 -*-
import os

class Config:
    DEBUG = True
    #SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost:3306/websnail'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)),'data.sqlite')
    SECRET_KEY = 'what does the fox say?'
    CODEMIRROR_LANGUAGES = ['python']
    CODEMIRROR_ADDONS = (
            ('display','placeholder'),
    )
    CODEMIRROR_THEME = 'mbo'
    WTF_CSRF_SECRET_KEY = "whatever"
    UPLOAD_FOLDER = "C:/Users/Administrator/Desktop/selftest/testplatform/app/static/uploads"
    CASE_FOLDER = "C:/Users/Administrator/Desktop/selftest/testplatform/testcases"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    APPIUM_LOG_LEVEL = "info"
    SHAIRED_CAPABILITIES = {
        "newCommandTimeout" : 120,
        "noSign" : True,
        "unicodeKeyboard":True,
        "resetKeyboard":True
    }

    #系统权限弹框中允许/拒绝按钮的id
    system_alerts = [
        ('com.huawei.systemmanager:id/btn_allow','com.huawei.systemmanager:id/btn_forbbid'),
        ('android:id/button1','android:id/button'),
        ('flyme:id/accept','flyme:id/reject')
    ]

    log_path = "C:/Users/Administrator/Desktop/selftest/testplatform/logs"
    snapshot_path = "C:/Users/Administrator/Desktop/selftest/testplatform/snapshots"

    monkey_action_count = 1000

    case_template = \
'''
# -*- coding: utf-8 -*-
import sys
sys.path.append("C:/Users/Administrator/Desktop/selftest/testplatform/app/main/defender/main")
from android.basecase import AndroidDevice
{% for lib in libs %}{{lib}};{% endfor %}

class TestCase(AndroidDevice):
    desc = "{{ desc }}"

    def __init__(self,ce,dc):
        self.dc = dc
        self.appium_port = ce['port']
        self.bootstrap_port = ce['bootstrap_port']
        self.device_name = dc['deviceName']
        self.appium_url = ce['url']
        self.filename = str(self.__class__).split('.')[0].split("\'")[1]
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
{% for action in actions %}
        {{ action }}
{% endfor %}
'''


    @staticmethod
    def init_app(app):
        pass
