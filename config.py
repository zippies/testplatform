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

    test_datas = \
    '''
    评价内容    |   [ "好好学习,天天向上!   " , "你行你上，不行别BB   " ]
    测试数据    |   "abcdef123456"
    '''

    conflict_datas = \
    '''
    登录帐号    |   [ ('11266661001','111111'), ('11266661002','111111'), ('11266661004','111111'),('11266661005','111111'),('11266661007','111111'),('11266661008','111111')]
    其他数据    |   [1,2]
    '''

    @staticmethod
    def init_app(app):
        pass
