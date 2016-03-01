# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,redirect,url_for,send_file,Response,session,flash
from ..models import db,Testjob,Appelement,Testcase,Device,Report,Testdata,Conflictdata
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
from multiprocessing import Process
from subprocess import Popen,PIPE
from . import main,AndroidRunner,MonkeyRunner,CompatibleRunner
from jinja2 import Template
from .. import Config
import os,sys,json,time,pickle,platform
sys.path.append(Config.CASE_FOLDER)

tasks = {}

@main.route("/")
@main.route("/index")
def index():
	'''
		首页导航
	'''
	pickle.dump(tasks,open("data/tasks.pkl",'wb'))
	devices = Device.query.all()
	testcases = Testcase.query.all()
	return render_template("index.html",
							deviceCount = len(devices),
							testcaseCount = len(testcases)
	)


@main.route("/getStatus")
def getStatus():
	task = {}
	try:
		task = pickle.load(open("data/tasks.pkl",'rb'))
	except:
		pass
	job = Testjob.query.filter_by(status=1).first()
	data = {"jobid":None,"status":None}
	if job:
		data["jobid"] = str(job.id)
		if str(job.id) not in session:
			session[str(job.id)] = "1"
		else:
			if task.values():
				result = task[str(job.id)]["result"]
				report = Report(
					-1 if len(result["success"]) != result['totalcount'] else 0,
					result["success"],
					result["failed"],
					result["duration"]
				)
				db.session.add(report)
				db.session.commit()
				job.status = 2
				job.reportID = report.id
				db.session.add(job)
				db.session.commit()
				data["status"] = "2"
				pickle.dump({},open("data/tasks.pkl",'wb'))
			else:
				data["status"] = "1"
	else:
		for jobid in task.keys():
			if jobid in session:
				session.clear()
			else:
				print("jobid not in session")

	data = json.dumps(data)

	return Response("data:"+data+"\n\n",mimetype="text/event-stream")


@main.route("/jobs")
def jobs():
	jobs = Testjob.query.all()
	return render_template("jobs.html",jobs=jobs[::-1])


@main.route("/newjob",methods=["POST","GET"])
def newjob():
	system = platform.system()
	if request.method == 'POST':
		try:
			choiceddevices = dict(request.form).get('choicedDevice')
			choicedcases = dict(request.form).get("choicedCase")
			jobname = request.form.get('jobName')
			testtype = request.form.get('testType')
			f = request.files['file']
			fname = secure_filename(f.filename)
			apk = os.path.join(Config.UPLOAD_FOLDER,fname)
			f.save(apk)
			cmd_activity = "aapt d badging %s|%s launchable-activity" %(apk,"findstr" if system == "Windows" else "grep")
			cmd_package = "aapt d badging %s|%s package" %(apk,"findstr" if system == "Windows" else "grep")
			activity = Popen(cmd_activity,stdout=PIPE,shell=True)
			package = Popen(cmd_package,stdout=PIPE,shell=True)
			main_activity = activity.stdout.read().decode().split("name='")[1].split("'")[0]
			packageName = package.stdout.read().decode().split("name='")[1].split("'")[0]
			activity.kill()
			package.kill()
			testjob = Testjob(jobname,testtype,choicedcases,choiceddevices,apk,packageName,main_activity)
			db.session.add(testjob)
			db.session.commit()
		except Exception as e:
			pass
		return redirect(url_for(".jobs"))
	else:
		pass
	return render_template("newjob.html")

@main.route("/deljob/<int:id>")
def deljob(id):
	try:
		job = Testjob.query.filter_by(id=id).first()
		if job:
			db.session.delete(job)
			db.session.commit()
			flash("删除成功！")
		else:
			flash("任务不存在")
	except Exception as e:
		flash("删除失败:%s" %str(e))
	finally:
		return redirect(url_for(".jobs"))

@main.route("/runjob/<int:id>",methods=["POST"])
def runjob(id):
	resp = {"result":True,"info":None}
	job = Testjob.query.filter_by(id=id).first()
	if job:
		jobtype = job.jobType
		try:
			if jobtype == 1:
				runCompatibilityTest(job)
			elif jobtype == 2:
				runStabilityTest(job)
			elif jobtype == 3:
				runFunctionalTest(job)
			else:
				pass
		except Exception as e:
			resp["result"] = False
			resp["info"] = "任务运行失败:%s" %str(e)
	else:
		resp["result"] = False
		resp["info"] = "任务不存在"
	return jsonify(resp)

def runCompatibilityTest(job):
	choiceddevices = []
	for deviceid in job.relateDevices:
		device = Device.query.filter_by(id=deviceid).first()
		if device.status == 0:
			choiceddevices.append(device)
	runner = CompatibleRunner(job.id,choiceddevices,job.testapk,job.appPackage,job.appActivity,Config.log_path,Config.snapshot_path)
	runner.start()
	job.status = 1
	db.session.add(job)
	db.session.commit()

class FakeDevice(object):
	def __init__(self,deviceName,platform,platformVersion):
		self.deviceName = deviceName
		self.platform = platform
		self.platformVersion = platformVersion

	def __repr__(self):
		return "<fakedevice:%s>" % self.deviceName

def runStabilityTest(job):
	choiceddevices = []
	for deviceid in job.relateDevices:
		device = Device.query.filter_by(id=deviceid).first()
		if device.status == 0:
			choiceddevices.append(FakeDevice(device.deviceName,device.platform,device.platformVersion))

	assert len(choiceddevices) > 0,"没有可用的设备"

	appelements = Appelement.query.all()
	testdatas = Testdata.query.all()
	conflict_datas = Conflictdata.query.all()

	capabilities = []
	for c_device in choiceddevices:
		capabilities.append({"deviceName":c_device.deviceName,"platformName":c_device.platform,"platformVersion":c_device.platformVersion})
	appiums = []
	testcases = {}
	under_testcase = []
	for index,device in enumerate(capabilities):
		for key,value in Config.SHAIRED_CAPABILITIES.items():
			device[key] = value
		device["app"] = job.testapk
		device["appPackage"] = job.appPackage
		device["appActivity"] = job.appActivity
		device['automationName'] = 'Appium' if float(device['platformVersion']) > 4.2 else 'Selendroid'
		device["newCommandTimeout"] = 60*60*24
		port = str(16230 + index)
		bootstrap_port = str(17230 + index)
		selendroid_port = str(15230 + index)
		appiums.append({"port":port,"bootstrap_port":bootstrap_port,"url":"http://localhost:%s/wd/hub" %port})
		under_testcase.append(__import__("defaultAction").TestCase(appiums[index],device))
	testcases["defaultAction"] = under_testcase
	androidRunner = AndroidRunner(
							job.id,
							testcases,
							appiums,
							Config.log_path,
							Config.snapshot_path,
							Config.APPIUM_LOG_LEVEL,
							Config.system_alerts,
							appelements,
							testdatas,
							conflict_datas,
							MonkeyRunner(job.id,choiceddevices,job.appPackage,job.testapk,Config.monkey_action_count,300,Config.log_path,Config.snapshot_path)
	)
	androidRunner.start()
	job.status = 1
	db.session.add(job)
	db.session.commit()

def runFunctionalTest(job):
	testcases = {}
	cases = [Testcase.query.filter_by(id=caseid).first() for caseid in job.relateCases]

	assert len(cases) > 0,"没有可用的测试用例"

	choiceddevices = []
	for deviceid in job.relateDevices:
		device = Device.query.filter_by(id=deviceid).first()
		if device.status == 0:
			choiceddevices.append(device)

	assert len(choiceddevices) > 0,"没有可用的设备"

	appelements = Appelement.query.all()
	testdatas = Testdata.query.all()
	conflict_datas = Conflictdata.query.all()

	capabilities = []
	for c_device in choiceddevices:
		capabilities.append({"deviceName":c_device.deviceName,"platformName":c_device.platform,"platformVersion":c_device.platformVersion})
	appiums = []
	for index,device in enumerate(capabilities):
		for key,value in Config.SHAIRED_CAPABILITIES.items():
			device[key] = value
		device["app"] = job.testapk
		device["appPackage"] = job.appPackage
		device["appActivity"] = job.appActivity
		device['automationName'] = 'Appium' if float(device['platformVersion']) > 4.2 else 'Selendroid'
		capabilities[index] = device
		port = str(16230 + index)
		bootstrap_port = str(17230 + index)
		selendroid_port = str(15230 + index)
		appiums.append({"port":port,"bootstrap_port":bootstrap_port,"url":"http://localhost:%s/wd/hub" %port})

	for case in cases:
		with open(os.path.join(Config.CASE_FOLDER,"%s.py" %case.caseName),'wb') as f:
			libs,actions = [],[]
			for c in case.caseContent.split("\r\n"):
				if c:
					libs.append(c) if c.startswith('from') or c.startswith("import") else actions.append(c)

			content = Template(Config.case_template.strip()).render(
				desc = case.caseDesc,
				libs = libs,
				actions = actions
			)
			f.write(str(content).encode('utf-8'))

		undertest_cases = []
		for index,device in enumerate(capabilities):
			undertest_cases.append(__import__(case.caseName).TestCase(appiums[index],device))
		testcases[case.caseName] = undertest_cases
	runner = AndroidRunner(
							job.id,
							testcases,
							appiums,
							Config.log_path,
							Config.snapshot_path,
							Config.APPIUM_LOG_LEVEL,
							Config.system_alerts,
							appelements,
							testdatas,
							conflict_datas	
	)
	runner.start()
	job.status = 1
	db.session.add(job)
	db.session.commit()

@main.route("/viewreport/<int:id>")
def viewreport(id):
	job = Testjob.query.filter_by(id=id).first()
	if job:
		report = Report.query.filter_by(id=job.reportID).first()
		if report:
			if job.jobType == 3:
				return render_template("report.html",
										jobtype=3,
										casecount=len(job.relateCases),
										devicecount=len(job.relateDevices),
										totalcount=len(job.relateCases)*len(job.relateDevices),
										successCases=report.successCases,
										failedCases=report.failedCases,
										success=len(report.successCases),
										failed=len(report.failedCases)
				)
			elif job.jobType == 2:
				return render_template("report.html",
										jobtype=2,
										casecount=0,
										devicecount=len(job.relateDevices),
										totalcount=len(job.relateDevices),
										successCases=report.successCases,
										failedCases=report.failedCases,
										success=len(report.successCases),
										failed=len(report.failedCases)
				)
			elif job.jobType == 1:
				return render_template("report.html",
										jobtype=1,
										casecount=0,
										devicecount=len(job.relateDevices),
										totalcount=len(job.relateDevices),
										successCases=report.successCases,
										failedCases=report.failedCases,
										success=len(report.successCases),
										failed=len(report.failedCases)
				)
			else:
				pass
		else:
			pass
	else:
		pass

	return "error"

@main.route("/getscreenshot")
def getscreenshot():
	imgfile = request.args.get("file")
	return send_file(imgfile,mimetype="image/png")

@main.route("/showapi")
def showapi():
	return render_template("api.html")