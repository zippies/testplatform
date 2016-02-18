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

    @staticmethod
    def init_app(app):
        pass
