# -*- coding: utf-8 -*-
from datetime import datetime
from . import db

class Testjob(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	jobName = db.Column(db.String(64))
	jobType = db.Column(db.Integer)   # 0:兼容性  1:稳定性  2:功能性
	relateDevices = db.Column(db.PickleType)
	testapk = db.Column(db.String(512))
	appPackage = db.Column(db.String(64))
	appActivity = db.Column(db.String(64))
	reportID = db.Column(db.Integer,default=0)
	appium_ports = db.Column(db.PickleType,default=[])
	status = db.Column(db.Integer,default=0)  # 0：未运行   1：正在运行  2：完成
	result = db.Column(db.Integer,default=0)  # 0:未运行    -1：失败   1：成功
	buildid = db.Column(db.Integer)
	caseorder = db.Column(db.PickleType)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,jobName,jobType,relateDevices,testapk,appPackage,appActivity,caseorder,buildid=0):
		self.jobName = jobName.strip()
		self.jobType = jobType
		self.relateDevices = relateDevices
		self.testapk = testapk
		self.appPackage = appPackage
		self.appActivity = appActivity
		self.caseorder = caseorder
		self.buildid = buildid

	def __repr__(self):
		return "<testjob:%s>" % self.jobName


class Report(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	result = db.Column(db.Integer)
	successCases = db.Column(db.PickleType)
	failedCases = db.Column(db.PickleType)
	runtime = db.Column(db.String(64))
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,result,successCases,failedCases,runtime):
		self.result = result
		self.successCases = successCases
		self.failedCases = failedCases
		self.runtime = runtime

class Device(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	phoneModel = db.Column(db.String(64))
	deviceName = db.Column(db.String(64))
	manufacturer = db.Column(db.String(64))
	platform = db.Column(db.String(64))
	platformVersion = db.Column(db.String(64))
	resolution = db.Column(db.String(64))
	status = db.Column(db.Integer,default=0)    #0:连接正常   -1：offline   -2：未授权   -3：未连接
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,phoneModel,deviceName,manufacturer,platform,platformVersion,resolution):
		self.phoneModel = phoneModel.strip()
		self.deviceName = deviceName.strip()
		self.manufacturer = manufacturer.strip()
		self.platform = platform.strip()
		self.platformVersion = platformVersion.strip()
		self.resolution = resolution.strip()

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
		self.caseName = caseName.strip()
		self.caseDesc = caseDesc.strip()
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

class Testdata(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	value = db.Column(db.PickleType)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,name,value):
		self.name = name.strip()
		self.value = value

	def __repr__(self):
		return "<Testdata:%s>" % self.name

class Conflictdata(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	value = db.Column(db.PickleType)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,name,value):
		self.name = name.strip()
		self.value = value

	def __repr__(self):
		return "<Conflictdata:%s>" % self.name

class Actionflow(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64))
	actions = db.Column(db.PickleType)
	createdtime = db.Column(db.DateTime,default=datetime.now)

	def __init__(self,name,actions):
		self.name = name.strip()
		self.actions = actions

	def __repr__(self):
		return "<Actionflow:%s>" %self.name