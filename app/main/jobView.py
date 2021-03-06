# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,redirect,url_for,send_file,Response,session,flash
from ..models import db,Testjob,Appelement,Testcase,Device,Report,Testdata,Conflictdata,Actionflow
from werkzeug.utils import secure_filename
from subprocess import Popen,PIPE
from collections import namedtuple,OrderedDict
from jinja2 import Template
from . import main,AndroidRunner,MonkeyRunner,CompatibleRunner,API
from .. import Config
import os,sys,json,time,pickle,platform,importlib,subprocess
sys.path.append(Config.CASE_FOLDER)

system = platform.system()
FakeDevice = namedtuple("FakeDevice","deviceName,platform,platformVersion")

@main.route("/")
@main.route("/index")
def index():
	'''
		首页导航
	'''
	if not os.path.isdir("data"):
		os.makedirs("data")

	devices = Device.query.all()
	testcases = Testcase.query.all()
	print(testcases)
	return render_template("index.html",
						    cases = testcases,
							deviceCount = len(devices),
							testcaseCount = len(testcases)
	)


@main.route("/getStatus")
def getStatus():
	global tasks
	task = {}
	try:
		task = pickle.load(open("data/tasks.pkl",'rb'))
	except:
		pass
	job = Testjob.query.filter_by(status=1).first()
	data = {"jobid":None,"status":None,"result":0}
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
				job.result = -1 if len(result["success"]) != result['totalcount'] else 1
				job.reportID = report.id
				db.session.add(job)
				db.session.commit()
				data["status"] = "2"
				data["result"] = -1 if len(result["success"]) != result['totalcount'] else 1
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
	timenow = time.strftime("%Y-%m-%d %H:%M:%S")
	cases = Testcase.query.all()
	return render_template("jobs.html",jobs=jobs[::-1],timenow=timenow,cases=cases)


@main.route("/newjob",methods=["POST"])
def newjob():
	choiceddevices = dict(request.form).get('choicedDevice')
	jobname = request.form.get('jobName')
	testtype = request.form.get('testType')

	monkeyconfig = {}
	monkeyconfig["actioncount"] = request.form.get("actioncount")
	monkeyconfig["actiondelay"] = request.form.get("actiondelay")
	monkeyconfig["touchpercent"] = request.form.get("touchpercent")
	monkeyconfig["motionpercent"] = request.form.get("motionpercent")
	monkeyconfig["pinchzoompercent"] = request.form.get("pinchzoompercent")
	monkeyconfig["majornavpercent"] = request.form.get("majornavpercent")
	monkeyconfig["syskeyspercent"] = request.form.get("syskeyspercent")
	monkeyconfig["appswitchpercent"] = request.form.get("appswitchpercent")

	order = request.args.get("order").split("|")
	f = request.files['file']
	fname = secure_filename(f.filename)
	apk = os.path.join(Config.UPLOAD_FOLDER,fname)
	if not os.path.isdir(Config.UPLOAD_FOLDER):
		os.makedirs(Config.UPLOAD_FOLDER)
	f.save(apk)
	cmd_activity = "aapt d badging %s|%s launchable-activity" %(apk,"findstr" if system == "Windows" else "grep")
	cmd_package = "aapt d badging %s|%s package" %(apk,"findstr" if system == "Windows" else "grep")
	activity = Popen(cmd_activity,stdout=PIPE,shell=True)
	package = Popen(cmd_package,stdout=PIPE,shell=True)
	main_activity = activity.stdout.read().decode().split("name='")[1].split("'")[0]
	packageName = package.stdout.read().decode().split("name='")[1].split("'")[0]
	activity.kill()
	package.kill()
	testjob = Testjob(jobname,testtype,choiceddevices,apk,packageName,main_activity,order,monkeyconfig)
	db.session.add(testjob)
	db.session.commit()
	return redirect(url_for(".jobs"))


@main.route("/deljob/<int:id>")
def deljob(id):
	try:
		job = Testjob.query.filter_by(id=id).first()
		if job:
			if job.status == 1:
				if job.jobType == 1:
					pass
				elif job.jobType == 2:
					devices = [device.deviceName for device in [Device.query.filter_by(id=deviceid).first() for deviceid in job.relateDevices]]
					for device in devices:
						searchcmd = "adb -s %s shell ps |grep com.android.commands.monkey" %device
						info = subprocess.run(searchcmd,stdout=PIPE)
						result = info.stdout.decode()
						if info.returncode == 0 and result:
							monkey_pid = [item for item in result.split(" ") if item.strip()][1]
							print(result,monkey_pid)
							killcmd = "adb -s %s shell kill -9 %s" %(device,monkey_pid)
							subprocess.run(killcmd,stdout=PIPE)
				elif job.jobType == 3:
					appium_ports = job.appium_ports
					for port in appium_ports:
						info = os.popen("netstat -ano|findstr %s" % port).readline()
						if "LISTENING" in info:
							pid = info.split("LISTENING")[1].strip()
							print("Stop pid:", pid)
							os.system("ntsd -c q -p %s" % pid)
				else:
					pass
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

def runStabilityTest(job):
	timestamp = job.createdtime.strftime("%y%m%d%H%M%S")

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
	defaultAction = importlib.reload(importlib.import_module("defaultAction"))
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
		under_testcase.append(defaultAction.TestCase(appiums[index],device))
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
							MonkeyRunner(job.id,timestamp,choiceddevices,job.appPackage,job.testapk,job.monkeyconfig,Config.log_path,Config.snapshot_path)
	)
	androidRunner.start()
	job.status = 1
	db.session.add(job)
	db.session.commit()

def runFunctionalTest(job):
	testcases = OrderedDict()
	appium_ports = []
	cases = [Testcase.query.filter_by(id=caseid).first() for caseid in job.caseorder]

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
		appium_ports.append(port)
		bootstrap_port = str(17230 + index)
		selendroid_port = str(15230 + index)
		appiums.append({"port":port,"bootstrap_port":bootstrap_port,"url":"http://localhost:%s/wd/hub" %port})

	reloaded = []

	for case in cases:
		generateCase(case)
		module = importlib.import_module(case.caseName)
		if case.caseName not in reloaded:
			module = importlib.reload(importlib.import_module(case.caseName))
			reloaded.append(case.caseName)
		undertest_cases = []

		for index,device in enumerate(capabilities):
			undertest_cases.append(module.TestCase(appiums[index],device))

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
	job.appium_ports = appium_ports
	job.status = 1
	job.result = 0
	db.session.add(job)
	db.session.commit()

def generateCase(case):
	with open(os.path.join(Config.CASE_FOLDER,"%s.py" %case.caseName),'wb') as f:
		libs,actions = [],[]
		for c in case.caseContent.split("\r\n"):
			if c:
				if c.strip().startswith('from') or c.strip().startswith("import"):
					libs.append(c.strip())
				elif c.strip().startswith("{{") and c.strip().endswith("}}"):
					whitespace = c.split("{{")[0]
					actionflow_name,args = c.strip().strip("{}").strip().split("(")
					args = args.strip("()").split(",")
					actionflow = Actionflow.query.filter_by(name=actionflow_name).first()
					if actionflow:
						flowactions = []
						for index,action in enumerate(actionflow.actions):
							for arg in args:
								if "{{%s}}" %arg in action:
									action = action.replace("{{%s}}" %arg,arg)
								else:
									continue

							flowactions.append(whitespace+action)

						actions += flowactions
				else:
					actions.append(c)
		content = Template(Config.case_template.strip()).render(
			desc = case.caseDesc,
			libs = libs,
			actions = actions
		)
		f.write(str(content).encode('utf-8'))


@main.route("/viewreport/<int:id>")
def viewreport(id):
	job = Testjob.query.filter_by(id=id).first()
	if job:
		report = Report.query.filter_by(id=job.reportID).first()
		if report:
			if job.jobType == 3:
				return render_template("report.html",
										jobtype=3,
										casecount=len(job.caseorder),
										devicecount=len(job.relateDevices),
										totalcount=len(job.caseorder)*len(job.relateDevices),
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
	funcs = dir(API)
	funcs.sort()
	selfapis,driverapis = [],[]
	for func in funcs:
		if not func.startswith("_"):
			doc = eval("API.%s" %func).__doc__
			if doc:
				doc = doc.replace("\n","<p>")
				doc = doc.replace("\t","&nbsp&nbsp&nbsp&nbsp")
				doc = doc.replace("driver","self")

				selfapis.append([func,doc]) if doc.startswith("[方法]") else driverapis.append([func,doc])

	return render_template("api.html",selfapis=selfapis,driverapis=driverapis)

@main.route("/stopjob/<int:id>")
def stopjob(id):
	info = {"result":True,"errorMsg":None}
	try:
		job = Testjob.query.filter_by(id=id).first()
		if job:
			if job.status == 1:
				if job.jobType == 1:
					pass
				elif job.jobType == 2:
					devices = [device.deviceName for device in
							   [Device.query.filter_by(id=deviceid).first() for deviceid in job.relateDevices]]
					for device in devices:
						searchcmd = "adb -s %s shell ps |grep com.android.commands.monkey" % device
						info = subprocess.run(searchcmd, stdout=PIPE)
						result = info.stdout.decode()
						if info.returncode == 0 and result:
							monkey_pid = [item for item in result.split(" ") if item.strip()][1]
							print(result, monkey_pid)
							killcmd = "adb -s %s shell kill -9 %s" % (device, monkey_pid)
							subprocess.run(killcmd, stdout=PIPE)
				elif job.jobType == 3:
					appium_ports = job.appium_ports
					for port in appium_ports:
						info = os.popen("netstat -ano|findstr %s" % port).readline()
						if "LISTENING" in info:
							pid = info.split("LISTENING")[1].strip()
							print("Stop pid:", pid)
							os.system("ntsd -c q -p %s" % pid)
				else:
					pass
				job.status == 0
				db.session.add(job)
				db.session.commit()
		else:
			info = {"result":False,"errorMsg":"任务不存在"}
	except Exception as e:
		info = {"result": False, "errorMsg": "删除失败:%s" % str(e)}
	finally:
		return jsonify(info)


@main.route("/newjobfromjenkins",methods=["POST"])
def newjobfromjenkins():
	#need modify
	info = {"result":True,"errorMsg":None}
	try:
		data = request.form
		apk = data.get("app")
		jobtype = data.get("type")
		choicedcases = dict(data).get("cases")
		choiceddevices = dict(data).get("devices")
		buildid = data.get("buildid")
		jobname = "Jenkins_AutomationTest_Build_%s" %buildid

		if "all" in choicedcases:
			choicedcases = [case.id for case in Testcase.query.filter_by(status=1).all()]
		else:
			try:
				choicedcases = eval(choicedcases[0])
			except:
				pass

			for caseid in choicedcases:
				if not Testcase.query.filter_by(id=caseid).first():
					assert 1==2,"id为'%s'的用例未创建或已被删除" %caseid

		for index,deviceid in enumerate(choiceddevices):
			device = Device.query.filter_by(id=deviceid).first()
			if not device:
				assert 1==2,"id为'%s'的设备未创建或已被删除" %deviceid

		cmd_activity = "aapt d badging %s|%s launchable-activity" %(apk,"findstr" if system == "Windows" else "grep")
		cmd_package = "aapt d badging %s|%s package" %(apk,"findstr" if system == "Windows" else "grep")
		activity = Popen(cmd_activity,stdout=PIPE,shell=True)
		package = Popen(cmd_package,stdout=PIPE,shell=True)
		main_activity = activity.stdout.read().decode().split("name='")[1].split("'")[0]
		packageName = package.stdout.read().decode().split("name='")[1].split("'")[0]
		activity.kill()
		package.kill()

		testjob = Testjob(jobname,jobtype,choiceddevices,apk,packageName,main_activity,choicedcases,Config.ci_monkeyconfig,buildid=buildid)
		db.session.add(testjob)
		db.session.commit()
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}

	return jsonify(info)

@main.route("/runjobfromjenkins/<build_id>")
def runjobfromjenkins(build_id):
	info = None
	job = Testjob.query.filter_by(buildid=build_id).first()
	if job:
		if job.status == 0:
			info = runJenkinsTest(job)
		else:
			info = {"result":False,"jobid":job.id,"errorMsg":"该任务已被运行,当前状态:%s" %job.status}
	else:
		info = {"result":False,"jobid":job.id,"errorMsg":"该任务未创建或已被删除"}

	return jsonify(info)


def runJenkinsTest(job):
	info = {"result":True,"jobid":job.id,"errorMsg":None}
	testcases = OrderedDict()
	cases = [Testcase.query.filter_by(id=caseid).first() for caseid in job.caseorder]

	if not len(cases) > 0:
		info = {"result":False,"jobid":job.id,"errorMsg":"没有可用的测试用例"}
		return info
	choiceddevices = []
	for deviceid in job.relateDevices:
		device = Device.query.filter_by(id=deviceid).first()
		if device.status == 0:
			choiceddevices.append(device)

	if not len(choiceddevices) > 0:
		info = {"result":False,"jobid":job.id,"errorMsg":"没有可用的设备"}
		return info

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

	reloaded = []

	for case in cases:
		generateCase(case)
		module = importlib.import_module(case.caseName)
		if case.caseName not in reloaded:
			module = importlib.reload(importlib.import_module(case.caseName))
			reloaded.append(case.caseName)
		undertest_cases = []

		for index,device in enumerate(capabilities):
			undertest_cases.append(module.TestCase(appiums[index],device))

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

	return info

@main.route("/getjobstatusfromjenkins/<buildid>")
def getjobstatusfromjenkins(buildid):
	info = {"result":True,"status":True,"jobid":None,"errorMsg":None}
	task = {}
	try:
		task = pickle.load(open("data/tasks.pkl",'rb'))
	except:
		pass
	job = Testjob.query.filter_by(buildid=buildid).first()
	if job:
		info["jobid"] = job.id
		if task.values():
			result = task[str(job.id)]["result"]
			info["status"] = False if len(result["success"]) != result['totalcount'] else True
			report = Report(
				-1 if len(result["success"]) != result['totalcount'] else 0,
				result["success"],
				result["failed"],
				result["duration"]
			)
			db.session.add(report)
			db.session.commit()
			job.status = 2
			job.result = -1 if len(result["success"]) != result['totalcount'] else 1
			job.reportID = report.id
			db.session.add(job)
			db.session.commit()
			pickle.dump({},open("data/tasks.pkl",'wb'))
		else:
			info = {"result":False,"errorMsg":"job is running.."}
	else:
		info = {"result":False,"errorMsg":"job is not exists！"}

	return jsonify(info)