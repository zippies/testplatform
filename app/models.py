# -*- coding: utf-8 -*-
from datetime import datetime
from . import db,login_manager
from flask.ext.login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(64),unique=True,index=True)
	username = db.Column(db.String(64),unique=True,index=True)
	password = db.Column(db.String(128))
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,email,username,password):
		self.email = email
		self.username = username
		self.password = password

	def __repr__(self):
		return "<user:%s>" % self.username


class Testjob(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	jobName = db.Column(db.String(64))
	jobType = db.Column(db.Integer)   # 0:兼容性  1:稳定性  2:功能性
	relateCases = db.Column(db.PickleType)
	relateDevices = db.Column(db.PickleType)
	result = db.Column(db.Integer,default=0)
	reportID = db.Column(db.Integer,default=0)
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,jobName,jobType,relateCases,relateDevices):
		self.jobName = jobName
		self.jobType = jobType
		self.relateCases = relateCases
		self.relateDevices = relateDevices

	def __repr__(self):
		return "<testjob:%s>" % self.jobName


class Device(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	phoneModel = db.Column(db.String(64))
	deviceName = db.Column(db.String(64))
	manufacturer = db.Column(db.String(64))
	platform = db.Column(db.String(64))
	platformVersion = db.Column(db.String(64))
	resolution = db.Column(db.String(64))
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,phoneModel,deviceName,manufacturer,platform,platformVersion,resolution):
		self.phoneModel = phoneModel
		self.deviceName = deviceName
		self.manufacturer = manufacturer
		self.platform = platform
		self.platformVersion = platformVersion
		self.resolution = resolution

	def __repr__(self):
		return "<device:%s>" % self.phoneModel

class Testcase(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	caseName = db.Column(db.String(64))
	caseDesc = db.Column(db.String(64))
	caseContent = db.Column(db.PickleType)
	status = db.Column(db.Integer,default=0)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,caseName,caseDesc,caseContent):
		self.caseName = caseName
		self.caseDesc = caseDesc
		self.caseContent = caseContent

	def __repr__(self):
		return "<testcase:%s>" % self.caseName

class Appelement(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	findby = db.Column(db.String(64))
	name = db.Column(db.String(64))
	value = db.Column(db.String(512))
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,findby,name,value):
		self.findby = findby
		self.name = name
		self.value = value

	def __repr__(self):
		return "<Appelement:%s>" % self.name