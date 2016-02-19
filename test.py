import json
a = '''
# -*- coding: utf-8 -*-
from main.android.basecase import AndroidDevice


class TestCase(AndroidDevice):
	desc = "测试用例"

	def __init__(self,ce,dc):
		self.dc = dc
		self.appium_port = ce['port']
		self.bootstrap_port = ce['bootstrap_port']
		self.device_name = dc['deviceName']
		self.appium_url = ce['url']
		self.filename = str(self.__class__).split('.')[0].split('\'')[1]
		self.casename = '%s_%s_%s' %(dc['deviceName'].replace('.','_').replace(":","_"),ce['port'],self.filename)

	def __call__(self,conflict_datas):
		super(TestCase,self).__init__(conflict_datas,command_executor=self.appium_url,desired_capabilities=self.dc)
		return self

	def run(self):
		self.implicitly_wait(10)

		self.sleep(10)
'''

print(__import__(a))