# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,redirect,url_for,send_file
from ..models import db,Testjob,Appelement,Testcase,Device,Report
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
from multiprocessing import Process
from subprocess import Popen,PIPE
from . import main,AndroidRunner
from .. import Config
import os,sys,json
sys.path.append(Config.CASE_FOLDER)

tasks = {}
json.dump(tasks,open("tasks.json",'w'))

@main.route("/")
@main.route("/index")
def index():
	deviceCount = 10
	testcaseCount = 75
	return render_template("index.html",
							deviceCount = deviceCount,
							testcaseCount = testcaseCount
	)

@main.route("/jobs")
def jobs():
	jobs = Testjob.query.all()
	return render_template("jobs.html",jobs=jobs)

@main.route("/newjob",methods=["POST","GET"])
def newjob():
	if request.method == 'POST':
		try:
			choiceddevices = dict(request.form).get('choicedDevice')
			choicedcases = dict(request.form).get("choicedCase")
			jobname = request.form.get('jobName')
			testtype = request.form.get('testType')
			print(choiceddevices,choicedcases,jobname,testtype)
			f = request.files['file']
			fname = secure_filename(f.filename)
			apk = os.path.join(Config.UPLOAD_FOLDER,fname)
			f.save(apk)
			cmd_activity = "aapt d badging %s|findstr launchable-activity" %apk
			cmd_package = "aapt d badging %s|findstr package" %apk
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

@main.route("/runjob/<int:id>",methods=["POST"])
def runjob(id):
	resp = {"result":True,"info":None}
	job = Testjob.query.filter_by(id=id).first()
	if job:
		jobtype = job.jobType
		try:
			if jobtype == 1:
				pass
			elif jobtype == 2:
				pass
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

@main.route("/getStatus/<int:id>")
def getStatus(id):
	tasks = json.load(open("tasks.json","r"))
	job = None
	resp = {}
	print("current_jobstate:",tasks)
	if tasks.keys():
		job = Testjob.query.filter_by(id=id).first() if id else Testjob.query.filter_by(status=1).first()
		if tasks[job.id] == 1:
			resp = {"status":1,"jobid":job.id}
		else:
			job.status = 2
			db.session.add(job)
			db.session.commit()
			resp = {"status":2,"jobid":job.id}
		return jsonify(resp)
	else:
		return ""


def runFunctionalTest(job):
	testcases = {}
	cases = [Testcase.query.filter_by(id=caseid).first() for caseid in job.relateCases]
	choiceddevices = [Device.query.filter_by(id=deviceid).first() for deviceid in job.relateDevices]
	appelements = Appelement.query.all()
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
		port = str(13230 + index)
		bootstrap_port = str(14230 + index)
		selendroid_port = str(15230 + index)
		appiums.append({"port":port,"bootstrap_port":bootstrap_port,"url":"http://localhost:%s/wd/hub" %port})

	for case in cases:
		with open(os.path.join(Config.CASE_FOLDER,"%s.py" %case.caseName),'wb') as f:
			f.write(str(case.caseContent).encode('utf-8'))
		undertest_cases = []
		for index,device in enumerate(capabilities):
			undertest_cases.append(__import__(case.caseName).TestCase(appiums[index],device))
		testcases[case.caseName] = undertest_cases
	runner = AndroidRunner(
							job.id,
							testcases,
							capabilities,
							appiums,
							Config.log_path,
							Config.snapshot_path,
							"info",
							Config.system_alerts,
							appelements,
							Config.test_datas,
							Config.conflict_datas	
	)

	runner.start()
	tasks = json.load(open("tasks.json",'r'))
	tasks[job.id] = 1
	json.dump(tasks,open("tasks.json",'w'))
	job.status = 1
	db.session.add(job)
	db.session.commit()


@main.route("/viewreport/<int:id>")
def viewreport(id):
	job = Testjob.query.filter_by(id=id).first()
	if job:
		report = Report.query.filter_by(id=job.reportID).first()
		if report:
			return render_template("report.html",
									casecount=len(job.relateCases),
									devicecount=len(job.relateDevices),
									totalcount=len(job.relateCases)*len(job.relateDevices),
									successCases=report.successCases,
									failedCases=report.failedCases,
									success=len(report.successCases),
									failed=len(report.failedCases)
			)
		else:
			pass
	else:
		pass

	return "error"

@main.route("/getscreenshot")
def getscreenshot():
	imgfile = request.args.get("file")
	return send_file(imgfile,mimetype="image/png")