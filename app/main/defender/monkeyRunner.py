# -*- coding: utf-8 -*-
from multiprocessing import Process,Manager
from threading import Thread
from datetime import datetime
import os,time,pickle

class Device(object):
	def __init__(self,id,deviceName):
		self.id = id
		self.deviceName = deviceName

	def __repr__(self):
		return "<Device:%s>" %self.deviceName

class Monkey(object):
	def __init__(self,device,packageName,apk,monkeyconfig,timestamp,logpath,snapshotpath):
		self.device = device
		self.packageName = packageName
		self.apk = apk
		self.timestamp = timestamp
		self.monkeyconfig = monkeyconfig
		self.actionCount = monkeyconfig["actioncount"]
		self.logpath = logpath
		self.snapshotpath = snapshotpath
		self.screenshotimgs = []
		self.runtime = 0
		self.logcontents = []
		self.errorMsg = None

	def runTest(self):
		logfile = os.path.join(self.logpath,"%s.log" %self.device.deviceName)

		cmd = "adb -s {deviceName} shell monkey -s {seed} -p {packageName} -v --pct-touch {touchpercent} --pct-motion {motionpercent} --pct-pinchzoom {pinchzoompercent} --pct-majornav {majornavpercent} --pct-syskeys {syskeyspercent} --pct-appswitch {appswitchpercent} --throttle {actionDelay} {actionCount} > {logfile}".format(
			deviceName=self.device.deviceName,
			seed=self.timestamp,
			packageName=self.packageName,
			touchpercent = self.monkeyconfig["touchpercent"],
			motionpercent = self.monkeyconfig["motionpercent"],
			pinchzoompercent = self.monkeyconfig["pinchzoompercent"],
			majornavpercent = self.monkeyconfig["majornavpercent"],
			syskeyspercent = self.monkeyconfig["syskeyspercent"],
			appswitchpercent = self.monkeyconfig["appswitchpercent"],
			actionDelay=self.monkeyconfig["actiondelay"],
			actionCount=self.monkeyconfig["actioncount"],
			logfile=logfile
		)
		
		start = time.time()
		os.system(cmd)
		end = time.time()
		self.runtime = round(end - start,2)
		with open(logfile,'r') as f:
			for line in f.readlines():
				if line.strip():
					self.logcontents.append(line.strip())
		self.save_screen("after_test")
		self.analysisResult(logfile)

	def save_screen(self,filename):
		file = "%s_%s" %(self.device.deviceName,filename)
		save = "adb -s {deviceName} shell /system/bin/screencap -p /sdcard/{file}.png".format(deviceName=self.device.deviceName,file=file)
		pull = "adb -s {deviceName} pull /sdcard/{file}.png {snapshotpath}".format(deviceName=self.device.deviceName,file=file,snapshotpath=self.snapshotpath)
		os.system(save)
		os.system(pull)
		self.screenshotimgs.append([file,os.path.join(self.snapshotpath,"%s.png" %file)])

	def analysisResult(self,logfile):
		with open(logfile,'r') as f:
			for line in f.readlines():
				if "aborted" in line or "Error" in line or "Failure" in line:
					self.errorMsg = line

class MonkeyRunner(Thread):
	def __init__(self,id,timestamp,devices,packageName,apk,monkeyconfig,logpath,snapshotpath):
		Thread.__init__(self)
		self.id = id
		self.logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.logpath = os.path.join(logpath,self.logtime)
		self.snapshotpath = os.path.join(snapshotpath,self.logtime)
		self.devices = devices
		self.monkeys = self._createMonkeys(packageName,apk,monkeyconfig,timestamp)
		self.result = {
			"totalcount":len(devices),
			"casecount":0,
			"duration":0,
			"success":[],
			"failed":[]
		}
		self._initdirs()

	def __repr__(self):
		return "<MonkeyRunner>"

	def _createMonkeys(self,packageName,apk,monkeyconfig,timestamp):
		monkeys = []
		for device in self.devices:
			monkey = Monkey(device,packageName,apk,monkeyconfig,timestamp,self.logpath,self.snapshotpath)
			monkeys.append(monkey)

		return monkeys

	def _initdirs(self):
		'''
			初始化(如果不存在则创建)日志文件夹路径和截图文件夹路径
		'''
		if not os.path.isdir(self.logpath):
			os.makedirs(self.logpath)
		if not os.path.isdir(self.snapshotpath):
			os.makedirs(self.snapshotpath)

	def run(self):
		threads = []
		for monkey in self.monkeys:
			t = Thread(target=monkey.runTest)
			t.setDaemon(True)
			threads.append(t)

		for t in threads:
			t.start()

		for t in threads:
			t.join()

		self.analysisResult()

	def analysisResult(self):
		for monkey in self.monkeys:
			if monkey.errorMsg:
				self.result["failed"].append(monkey)
			else:
				self.result["success"].append(monkey)

			self.result["duration"] += monkey.runtime

		tasks = {str(self.id):{"status":"2","result":self.result}}

		with open("data/tasks.pkl","wb") as f:
			pickle.dump(tasks,f)
