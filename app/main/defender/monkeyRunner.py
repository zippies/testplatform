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
	def __init__(self,device,packageName,apk,actionCount,actionDelay,logpath,snapshotpath):
		self.device = device
		self.packageName = packageName
		self.apk = apk
		self.actionDelay = actionDelay
		self.actionCount = actionCount
		self.logpath = logpath
		self.snapshotpath = snapshotpath
		self.screenshotimgs = []
		self.runtime = 0
		self.logcontents = []
		self.errorMsg = None

	def runTest(self):
		logfile = os.path.join(self.logpath,"%s.log" %self.device.deviceName)

		# self.logcontents.append("[action]Try to uninstall old apk:%s" %self.packageName)
		# uninstall_history_pkg = "adb -s {deviceName} uninstall {packageName}".format(deviceName=self.device.deviceName,packageName=self.packageName)
		# infos = os.popen(uninstall_history_pkg).readlines()
		# for info in infos:
		# 	if info.strip():
		# 		if info.strip()== "Success":
		# 			self.logcontents.append("[status]uninstall old apk success")
		# 		else:
		# 			self.logcontents.append("[status]apk not installed,continue...")
		
		# self.save_screen("before_install_apk")

		# self.logcontents.append("[action]Try to install new apk:%s" %self.apk)
		# install_pkg = "adb -s {deviceName} install {apk}".format(deviceName=self.device.deviceName,apk=self.apk)
		# infos = os.popen(install_pkg).readlines()
		# for info in infos:
		# 	if info.strip():
		# 		if "Failure" in info.strip() or "Error" in info.strip() or "Missing" in info.strip():
		# 			self.errorMsg = "install apk failed!"
		# 		else:
		# 			self.logcontents.append("[status]installing apk:%s" %info.strip())

		# self.save_screen("after_install_apk")

		cmd = "adb -s {deviceName} shell monkey -s {seed} -p {packageName} -v --throttle {actionDelay} {actionCount} > {logfile}".format(
			deviceName=self.device.deviceName,
			seed=123,
			packageName=self.packageName,
			actionDelay=self.actionDelay,
			actionCount=self.actionCount,
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
	def __init__(self,id,devices,packageName,apk,actionCount,actionDelay,logpath,snapshotpath):
		Thread.__init__(self)
		self.id = id
		self.logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.logpath = os.path.join(logpath,self.logtime)
		self.snapshotpath = os.path.join(snapshotpath,self.logtime)
		self.devices = devices
		self.monkeys = self._createMonkeys(packageName,apk,actionCount,actionDelay)

		self.packageName = packageName
		self.actionCount = actionCount
		self.actionDelay = actionDelay
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

	def _createMonkeys(self,packageName,apk,actionCount,actionDelay):
		monkeys = []
		for device in self.devices:
			monkey = Monkey(device,packageName,apk,actionCount,actionDelay,self.logpath,self.snapshotpath)
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


if __name__ == "__main__":
	devices = [Device(1,"M3LDU15424001636")]
	runner = MonkeyRunner(
		1,
		devices,
		"com.wenba.bangbang",
		100,
		300,
		"C:/Users/Administrator/Desktop/selftest/testplatform/logs",
		"C:/Users/Administrator/Desktop/selftest/testplatform/snapshots"
	)
	runner.start()
	runner.join()