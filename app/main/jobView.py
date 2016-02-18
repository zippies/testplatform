# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,redirect,url_for
from . import main
from .. import Config
from ..models import db,Testjob
from subprocess import Popen,PIPE
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
import os

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
			testjob = Testjob(jobname,testtype,choicedcases,choiceddevices)
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
		startJob(jobtype)
	else:
		resp["result"] = False
		resp["info"] = "任务不存在"
	return jsonify(resp)

def startJob(jobtype):
	ispass = True
	if jobtype == 1:
		pass
	elif jobtype == 2:
		pass
	elif jobtype == 3:
		pass
	else:
		pass

	return ispass