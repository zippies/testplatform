# -*- coding: utf-8 -*-
from flask import Flask,render_template
from flask.ext.bootstrap import Bootstrap
from config import Config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()

def createApp():
	app = Flask(__name__)
	config = Config()
	app.config.from_object(config)
	config.init_app(app)
	bootstrap.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	from .main import main as BluePrint
	app.register_blueprint(BluePrint)

	return(app)