# -*- coding: utf-8 -*-
import sys,os,time,requests,platform,pickle
from .main import Logger,TestData,CaseElements
from multiprocessing import Process
from threading import Thread
from datetime import datetime
from pprint import pprint

class CaseObject(object):
	def __init__(self,case):
		self.casename = case.casename
		self.casedesc = case.desc
		self.runtime = round(case.result['runtime'],2)
		self.errorMsg = case.result['errorMsg']
		self._processSelf(case)

	def _processSelf(self,case):
		if os.path.exists(case.appiumlogfile):
			with open(case.appiumlogfile,'r') as f:
				self.appiumlogcontent = f.readlines()
		else:
			self.appiumlogcontent = ['appium log did not generated,check "androidConfig.py" whether "appium_log_level" has been set to "error",try "info" or "debug" instead']
		if os.path.exists(case.caselogfile):
			with open(case.caselogfile,'r') as f:
				self.caselogcontent = f.readlines()
		else:
			self.caselogcontent = ['no case action recorded']

		self.screenshotimgs = [[file,os.path.join(case.screenshotdir,file)] for file in os.listdir(case.screenshotdir)]

	def __repr__(self):
		return "<CaseObject:%s>" %self.casename 

class AndroidRunner(Process):
	def __init__(self,
				id,
				cases,
				capabilities,
				appiums,
				logpath,
				snapshotpath,
				appium_log_level,
				system_alert_ids,
				case_elements,
				test_datas,
				conflict_datas):
		Process.__init__(self)
		self.id = id
		self.cases = cases
		self.capabilities = capabilities
		self.reachable_devices = None
		self.appium_log_level = appium_log_level
		self.snapshotpath = snapshotpath
		self.current_system = platform.system()
		self.system_alert_ids = system_alert_ids
		self.case_elements = CaseElements(case_elements)
		self.test_datas = TestData(test_datas)
		self.conflict_datas = self._parseConflictData(conflict_datas)
		self.current_time = time.time()
		self.logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		self.appiums = appiums
		self.logdir = os.path.join(logpath,self.logtime)
		self.result = {
				"success":[],
				"failed":[],
				"totalcount":0,
				"casecount":0,
				"duration":0
		}
		self._initdirs()

	def __repr__(self):
		return "<AndroidRunner>"

	def _initdirs(self):
		'''
			初始化(如果不存在则创建)日志文件夹路径和截图文件夹路径
		'''
		os.makedirs(self.logdir)

		for cases in self.cases.values():
			self.result['casecount'] += 1
			self.result['totalcount'] += len(cases)
			for case in cases:
				case_screenshot = os.path.join(self.snapshotpath,case.casename,self.logtime)
				os.makedirs(case_screenshot)
				setattr(case,'screenshotdir',case_screenshot)

	def _parseConflictData(self,conflict_datas):
		datas = {}
		for data in conflict_datas:
			datas[data.name] = data.value

		return datas

	def is_Appium_Alive(self,port):
		'''
			检查指定端口的appium是否已启动
		'''
		try:
			r = requests.get('http://localhost:%s/wd/hub' %port)
			if r.status_code == 404:
				return True
			else:
				return False
		except Exception as e:
			return False

	def startAppium(self,cases,timeout=30):
		'''
			每个连接的设备(手机)对应启动一个appium服务
		'''
		appium_process_list = []
		for case in cases:
			appiumlog = os.path.join(self.logdir,case.device_name + "_" + case.appium_port + case.filename + "_appium.log")
			cmd = "appium\
					 -a 127.0.0.1 \
					 -p %s \
					 -bp %s \
					 -g %s \
					 --log-timestamp \
					 --log-level %s \
					 -U %s \
					 --log-no-colors > %s.txt" %(case.appium_port,case.bootstrap_port,appiumlog,self.appium_log_level,case.device_name,case.appium_port)
			p = Process(target=os.system,args=(cmd,))
			p.daemon = True
			appium_process_list.append(p)
			if self.is_Appium_Alive(case.appium_port):
				self.stopAppium()
			print("[action]Starting Appium on port : %s bootstrap_port: %s for device %s" %(case.appium_port,case.bootstrap_port,case.device_name))

		for p in appium_process_list:
			p.start()

		for case in cases:
			starts = time.time()
			while time.time() - starts < timeout:
				if self.is_Appium_Alive(case.appium_port):
					print("[success]Appium started on port : %s bootstrap_port: %s for device %s" %(case.appium_port,case.bootstrap_port,case.device_name))
					break
				else:
					time.sleep(0.5)
			else:
				print("[failure]Start Appium failed on port: %s bootstrap_port: %s for device %s!" %(case.appium_port,case.bootstrap_port,case.device_name))
				self.stopAppium()
				sys.exit(-1)

	def stopAppium(self):
		'''
			关闭所有appium服务
		'''
		if self.current_system == 'Windows':
			os.system("taskkill /F /IM node.exe")
		else:
			os.system("killall node")

	def run(self):
		'''
			运行所有测试用例
		'''
		try:
			for cases in self.cases.values():
				self.startAppium(cases)
				testjobs = []

				for case in cases:
					t = Thread(target=self.runTest,args=(case,self.conflict_datas))
					testjobs.append(t)

				for job in testjobs:
					job.start()

				for job in testjobs:
					job.join()
		except Exception as e:
			print("error occured while running 'runMultiTest':",str(e))
		finally:
			time.sleep(1)
			self.stopAppium()
			tasks = {str(self.id):{"status":"2","result":self.result}}
			with open("tasks.pkl","wb") as f:
				pickle.dump(tasks,f)

	def runTest(self,case,conflict_datas):
		print("[action]Initializing case %s" %case.casename)
		start = time.time()
		initsuccess = False
		caselog = os.path.join(self.logdir,case.casename+"_case")
		logger = Logger(caselog)
		setattr(case, 'logger',logger)
		setattr(case, 'result', {"errorMsg":None})
		setattr(case, 'appiumlogfile', os.path.join(self.logdir,case.device_name+"_"+case.appium_port+case.filename+"_appium.log"))
		setattr(case, 'caselogfile',caselog+"_info.log")
		setattr(case, 'case_elements',self.case_elements)
		setattr(case, 'test_datas',self.test_datas)
		setattr(case, 'system_alert_ids',self.system_alert_ids)
		try:
			case = case(conflict_datas)
			initsuccess = True
			print("[action]running test:%s %s" %(case.casename,case.desc))
			case.run()
			case.result['result'] = True
		except Exception as e:
			print(e)
			errorMsg = str(e)
			case.logger.log("[ERROR]%s" %errorMsg)
			if initsuccess:
				case.save_screen("error")
			case.result['result'] = False
			case.result['errorMsg'] = errorMsg
		finally:
			case.save_screen("end")
			end = time.time()
			case.result['runtime'] = round(end-start,2)
			self.result['duration'] += case.result['runtime']
			if case.result['result']:
				self.result['success'].append(CaseObject(case))
			else:
				self.result['failed'].append(CaseObject(case))
			print("end test:",case.casename)
			if initsuccess:
				case.close_app()
				case.quit()