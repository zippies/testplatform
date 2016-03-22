# -*- coding: utf-8 -*-
from app import createApp,db
from flask import render_template,flash,redirect,url_for
from app.models import *
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand
from werkzeug.contrib.fixers import ProxyFix
import pickle,os,sys

app = createApp()
app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

@manager.command
def dbinit():
	db.create_all()
	print('dbinit ok')

@manager.command
def dbdrop():
	db.drop_all()
	print('ok')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.errorhandler(401)
def unauthorized(e):
	flash({"type":"info","message":"请登陆后访问！"})
	return redirect(url_for(".login"))

if __name__ == '__main__':
	if not os.path.isdir("data"):
		os.mkdir("data")
	pickle.dump({},open("data/tasks.pkl",'wb'))
	if not os.path.exists("data.sqlite") and sys.argv[1] == "runserver":
		print("[error]数据库尚未初始化，请先运行:python manager.py dbinit")
	else:
		manager.run()