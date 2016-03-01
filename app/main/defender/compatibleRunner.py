# -*- coding: utf-8 -*-
from multiprocessing import Process,Manager
from threading import Thread
from datetime import datetime
from .main import Logger
from pprint import pprint
import os,time,pickle

class Device(object):
	def __init__(self,id,deviceName):
		self.id = id
		self.deviceName = deviceName

	def __repr__(self):
		return "<Device:%s>" %self.deviceName

class Compatibler(object):
	def __init__(self,device,apk,packageName,appActivity,logpath,snapshotpath):
		self.device = device
		self.apk = apk
		self.packageName = packageName
		self.appActivity = appActivity
		self.logfile = os.path.join(logpath,"compatibler.log")
		self.snapshotpath = snapshotpath
		self.screenshotimgs = []
		self.runtime = 0
		self.logcontents = []
		self.errorMsg = None

	def runTest(self):
		start = time.time()
		self.logcontents.append("[action]Try to uninstall old apk:%s" %self.packageName)
		uninstall_history_pkg = "adb -s {deviceName} uninstall {packageName}".format(deviceName=self.device.deviceName,packageName=self.packageName)
		infos = os.popen(uninstall_history_pkg).readlines()
		for info in infos:
			if info.strip():
				if info.strip()== "Success":
					self.logcontents.append("[status]uninstall old apk success")
				else:
					self.logcontents.append("[status]apk not installed,continue...")
		
		self.save_screen("before_install_apk")

		self.logcontents.append("[action]Try to install new apk:%s" %self.apk)
		install_pkg = "adb -s {deviceName} install {apk}".format(deviceName=self.device.deviceName,apk=self.apk)
		infos = os.popen(install_pkg).readlines()
		for info in infos:
			if info.strip():
				if "Failure" in info.strip() or "Error" in info.strip() or "Missing" in info.strip():
					self.errorMsg = "install apk failed!"
				else:
					self.logcontents.append("[status]installing apk:%s" %info.strip())

		self.save_screen("after_install_apk")

		self.logcontents.append("[action]Try to call up app with package: %s,activity:%s" %(self.packageName,self.appActivity))
		call_up_app = "adb -s {deviceName} shell am start -n {packageName}/{appActivity}".format(deviceName=self.device.deviceName,packageName=self.packageName,appActivity=self.appActivity)
		infos = os.popen(call_up_app).readlines()
		for info in infos:
			if info.strip():
				if "Failure" in info.strip() or "Error" in info.strip():
					self.errorMsg = "call up apk failed!"
				else:
					self.logcontents.append("[status]%s" %info.strip())
					self.logcontents.append("[status]Success")

		time.sleep(2)
		self.save_screen("call_up_app")

		self.logcontents.append("[action]Try to uninstall new apk:%s" %self.packageName)
		uninstall_history_pkg = "adb -s {deviceName} uninstall {packageName}".format(deviceName=self.device.deviceName,packageName=self.packageName)
		infos = os.popen(uninstall_history_pkg).readlines()
		for info in infos:
			if info.strip():
				if "Failure" in info.strip() or "Error" in info.strip():
					self.errorMsg = "uninstall apk failed!"
				else:
					self.logcontents.append("[status]%s" %info.strip())

		self.save_screen("uninstall_app")

		end = time.time()
		self.runtime = round(end - start,2)

	def save_screen(self,filename):
		file = "%s_%s" %(self.device.deviceName,filename)
		save = "adb -s {deviceName} shell /system/bin/screencap -p /sdcard/{file}.png".format(deviceName=self.device.deviceName,file=file)
		pull = "adb -s {deviceName} pull /sdcard/{file}.png {snapshotpath}".format(deviceName=self.device.deviceName,file=file,snapshotpath=self.snapshotpath)
		os.system(save)
		os.system(pull)
		self.screenshotimgs.append([file,os.path.join(self.snapshotpath,"%s.png" %file)])

class CompatibleRunner(Process):
	def __init__(self,id,devices,apk,packageName,appActivity,logpath,snapshotpath):
		Process.__init__(self)
		self.id = id
		self.devices = devices
		self.apk = apk
		self.packageName = packageName
		self.appActivity = appActivity
		self.logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.logpath = os.path.join(logpath,self.logtime)
		self.snapshotpath = os.path.join(snapshotpath,self.logtime)
		self._initdirs()
		self.compatiblers = self._createCompatiblers()
		self.result = {
			"totalcount":len(devices),
			"casecount":0,
			"duration":0,
			"success":[],
			"failed":[]
		}

	def __repr__(self):
		return "<CompatibleRunner>"

	def _createCompatiblers(self):
		compatiblers = []
		for device in self.devices:
			compatibler = Compatibler(device,self.apk,self.packageName,self.appActivity,self.logpath,self.snapshotpath)
			compatiblers.append(compatibler)

		return compatiblers

	def _initdirs(self):
		'''
			初始化(如果不存在则创建)日志文件夹路径和截图文件夹路径
		'''
		os.makedirs(self.logpath)
		os.makedirs(self.snapshotpath)

	def run(self):
		threads = []
		for compatibler in self.compatiblers:
			t = Thread(target=compatibler.runTest)
			t.setDaemon(True)
			threads.append(t)

		for t in threads:
			t.start()

		for t in threads:
			t.join()

		self.analysisResult()

	def analysisResult(self):
		for compatibler in self.compatiblers:
			if compatibler.errorMsg:
				self.result["failed"].append(compatibler)
			else:
				self.result["success"].append(compatibler)

			self.result["duration"] += compatibler.runtime

		tasks = {str(self.id):{"status":"2","result":self.result}}

		with open("data/tasks.pkl","wb") as f:
			pickle.dump(tasks,f)

if __name__ == "__main__":
	devices = [Device(1,"M3LDU15424001636")]
	runner = CompatibleRunner(
		1,
		devices,
		"C:\\Users\\Administrator\\Downloads\\apks\\backup.apk",
		"com.wenba.bangbang",
		"C:/Users/Administrator/Desktop/selftest/testplatform/logs",
		"C:/Users/Administrator/Desktop/selftest/testplatform/snapshots"
	)
	runner.start()
	runner.join()