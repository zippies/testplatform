# -*- coding: utf-8 -*-
from appium import webdriver
from appium.webdriver.mobilecommand import MobileCommand as Command
from appium.webdriver.errorhandler import MobileErrorHandler
from appium.webdriver.switch_to import MobileSwitchTo
from appium.webdriver.webelement import WebElement as MobileWebElement
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os,time,random


class ActionTimeOut(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

class CheckError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

class CaseError(Exception):
	def __init__(self,info):
		self.info = info

	def __str__(self):
		return self.info

# Returns abs path relative to this file and not cwd
PATH = lambda p: os.path.abspath(
	os.path.join(os.path.dirname(__file__), p)
)

class AndroidDevice(webdriver.Remote):
	def __init__(self,conflict_datas,command_executor='http://localhost:4723/wd/hub',desired_capabilities=None,browser_profile=None,proxy=None,keep_alive=False):
		super(AndroidDevice,self).__init__(command_executor, desired_capabilities,browser_profile,proxy,keep_alive) #连接Appium服务
		self._session_url = command_executor
		self.screen_shots = 0
		self.device_width = self.get_window_size()['width']
		self.device_height = self.get_window_size()['height']
		self.conflict_datas = conflict_datas
		if self.command_executor is not None:
			self._addCommands()

		self.error_handler = MobileErrorHandler()
		self._switch_to = MobileSwitchTo(self)

		# add new method to the `find_by_*` pantheon
		By.IOS_UIAUTOMATION = MobileBy.IOS_UIAUTOMATION
		By.ANDROID_UIAUTOMATOR = MobileBy.ANDROID_UIAUTOMATOR
		By.ACCESSIBILITY_ID = MobileBy.ACCESSIBILITY_ID

	def __repr__(self):
		return "<TestCase>:"+self.casename
#=============================================自定义方法  BEGIN ==============================================================
	def randomInt(self,length=8):
		a = eval("1" + "0" * (length - 1))
		b = eval("1" + "0" * length) - 1
		return random.randint(a, b)

	def randomPhoneNum(self):
		phonepres = [134, 135, 136, 137, 138, 139, 150, 151, 152, 157, 158, 159, 182, 183, 184, 187, 188, 178, 147, 130,
					 131, 132, 155, 156, 185, 186, 176, 145, 133, 153, 180, 181, 189, 177]
		pre = random.sample(phonepres, 1)[0]
		after = self.randomInt(8)
		return "%s%s" % (pre, after)

	def log(self,info):
		'''[方法]
log(info)
向日志中写入内容，该内容会在报告中显示
用法：
	self.log("hello,chris")
		'''
		self.logger.log("[log]%s" %info)

	def sleep(self,seconds):
		'''[方法]
sleep(seconds)
睡眠几秒
参数：
	seconds：睡眠时间，单位秒
用法：
	self.sleep(10)
		'''
		self.logger.log("[action]sleep(seconds='%s')" %seconds)
		time.sleep(seconds)

	def find(self,by,value,nocheck=False):
		'''[方法]
find(by,value,nocheck=False)
查找一个元素
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	nocheck：如果该值为True,则元素找不到时忽略错误继续执行
用法：
	element = self.find('id','element_id')
	element = self.find('name','element_name')
	element = self.find('class_name','element_class_name')
	element = self.find('xpath','element_xpath')
	...
		'''
		if by not in ['id','accessibility_id','class_name','css_selector','name','link_text','partial_link_text','tag_name','xpath','ios_uiautomation','android_uiautomator']:
			raise CaseError("'find' function doesn't support such type:'%s'" %by)

		try:
			ele = eval("self.find_element_by_%s" %by)(value)
			return ele
		except Exception as e:
			if not nocheck:
				raise CaseError("Element not found using '%s' : %s" %(by,value))
			else:
				return None
		
	def finds(self,by,value,nocheck=False):
		'''[方法]
finds(by,value,nocheck=False)
查找多个元素
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	nocheck：如果该值为True,则元素找不到时忽略错误继续执行
用法：
	elements = self.finds('id','element_id')
	elements = self.finds('name','element_name')
	elements = self.finds('class_name','element_class_name')
	elements = self.finds('xpath','element_xpath')
	...
		'''
		if by not in ['id','accessibility_id','class_name','css_selector','name','link_text','partial_link_text','xpath','ios_uiautomation','android_uiautomator']:
			raise CaseError("'find' function doesn't support such type:'%s'" %by)

		eles = None

		try:
			eles = eval("self.find_elements_by_%s" %by)(value)
		except Exception as e:
			if not nocheck:
				raise CheckError("Elements not found using '%s' : %s" %(by,value))
			else:
				return []
		finally:
			if not eles:
				if not nocheck:
					raise CheckError("Elements not found using '%s' : %s" %(by,value))
				else:
					return []
			else:
				return eles

	def click(self,by,value,desc="",nocheck=False):
		'''[方法]
click(by,value,desc="",nocheck=False)
点击一个元素
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	desc：描述元素的文本信息，便于在日志中区别
	nocheck：如果该值为True,则元素找不到时忽略错误继续执行
用法：
	self.click('id','element_id')
	self.click('name','element_name')
	self.click('class_name','element_class_name')
	self.click('xpath','element_xpath')
	...
		'''
		self.logger.log("[action]click(by='%s',value='%s',nocheck=%s) '%s'" %(by,value,nocheck,desc))
		if not isinstance(value, str):
			raise CaseError("'click' function required a str type on 'value' parameter")

		ele = self.find(by,value,nocheck)
		
		if not ele and nocheck:
			return None
		else:
			ele.click()

	def save_screen(self,filename=None,immediate=False):
		'''[方法]
save_screen(filename=None,immediate=False)
保存屏幕截图
参数：
	filename: 截图存储的文件名,若不提供则默认从1开始为截图命名
	immediate：如果该值为False 则会等待两秒后再截图
用法：
	self.save_screen()
	self.save_screen('filename')
	self.save_screen('filename',immediate=True)
		'''
		time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		screen = None
		if filename:
			screen = os.path.join(self.screenshotdir,"%s_%s.png" %(time_str,filename))
		else:
			self.screen_shots += 1
			screen = os.path.join(self.screenshotdir,"%s_%s.png" %(time_str,self.screen_shots))
		if not immediate:
			self.sleep(2)
		self.logger.log("[action]save_screen(filename='%s',immediate=%s)" %(screen,immediate))
		self.get_screenshot_as_file(screen)

	def input(self,by,value,text,desc="",nocheck=False):
		'''[方法]
input(by,value,text,desc="",nocheck=False)
向一个元素内输入内容
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	test：输入的文本内容
	desc：描述元素的文本信息，便于在日志中区别
	nocheck：如果该值为True,则元素找不到时忽略错误继续执行
用法：
	self.input('id','element_id',"文本内容")
	self.input('name','element_name',"文本内容")
	self.input('class_name','element_class_name',"文本内容")
	self.input('xpath','element_xpath',"文本内容")
	...
		'''
		self.logger.log("[action]input(by='%s',value='%s',text='%s',nocheck=%s) '%s'" %(by,value,text,nocheck,desc))
		ele = self.find(by,value,nocheck)
		if not ele and nocheck:
			return None
		else:
			ele.send_keys(text)

	def gettext(self,by,value,desc="",nocheck=False):
		'''[方法]
gettext(by,value,desc="",nocheck=False)
向一个元素内输入内容
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	desc：描述元素的文本信息，便于在日志中区别
	nocheck：如果该值为True,则元素找不到时忽略错误继续执行
用法：
	text = self.gettext('id','element_id',"描述元素内容")
	text = self.gettext('name','element_name',"描述元素内容")
	text = self.gettext('class_name','element_class_name',"描述元素内容")
	text = self.gettext('xpath','element_xpath',"描述元素内容")
	...
		'''
		self.logger.log("[action]gettext(by='%s',value='%s',nocheck=%s) '%s'" %(by,value,nocheck,desc))
		ele = self.find(by,value,nocheck)

		if not ele and nocheck:
			return None
		else:
			return ele.text

	def waitfor(self,by,value,desc="",timeout=10):
		'''[方法]
waitfor(by,value,desc="",timeout=10)
向一个元素内输入内容
参数：
	by：定位元素的方式/id/name/xpath/class_name等
	value：定位元素的id/name/xpath/class_name等的值
	desc：描述元素的文本信息，便于在日志中区别
	timeout：等待超时时间，单位秒
用法：
	self.waitfor('id','element_id',"描述元素内容")
	self.waitfor('name','element_name',"描述元素内容")
	self.waitfor('class_name','element_class_name',"描述元素内容")
	self.waitfor('xpath','element_xpath',"描述元素内容")
	...
		'''
		self.logger.log("[action]waitfor(by='%s',value='%s',timeout=%s) '%s'" %(by,value,timeout,desc))
		try:
			WebDriverWait(self,timeout,1).until(
				lambda x: getattr(x,'find_element_by_%s' %by)(value).is_displayed()
			)
			return self.find(by,value)
		except:
			raise ActionTimeOut("'%s:%s' element not shown after %s seconds '%s'" %(by,value,timeout,desc))

	def swipe(self,begin,end,duration=None):
		"""[方法]
swipe(begin,end,duration=None)
从一个点滑动到另一个点
参数:
	begin：开始点的坐标，例：(100,100)
	end：结束点的坐标，例：(100,400)
	duration：滑动操作持续的时间
用法:
	self.swipe((100, 100), (100, 400))
		"""
		# `swipe` is something like press-wait-move_to-release, which the server
		# will translate into the correct action
		self.logger.log("[action]swipe(begin=%s,end=%s,duration=%s)" %(begin,end,duration))
		start_x, start_y = begin
		end_x, end_y = end
		self.logger.log("%s %s %s %s" %(start_x,start_y,end_x,end_y))
		action = TouchAction(self)
		self.logger.log("action:%s" %action)
		action \
			.press(x=start_x, y=start_y) \
			.wait(ms=duration) \
			.move_to(x=end_x, y=end_y) \
			.release()
		action.perform()
		return self

	def swipe_up(self,duration=None):
		'''[方法]
swipe_up(duration=None)
从屏幕中间向上划半个屏幕高度
参数：
	duration：滑动操作持续的时间
用法：
	self.swipe_up()
		'''
		start = (self.device_width/2,self.device_height-10)
		end = (self.device_width/2,10)
		self.swipe(start,end,duration)

	def swipe_down(self,duration=None):
		'''[方法]
swipe_down(duration=None)
从屏幕中间向下划半个屏幕高度
参数：
	duration：滑动操作持续的时间
用法：
	self.swipe_down()
		'''
		start = (self.device_width/2,10)
		end = (self.device_width/2,self.device_height-10)
		self.swipe(start,end,duration)

	def swipe_left(self,duration=None):
		'''[方法]
swipe_left(duration=None)
从屏幕中间向左划半个屏幕宽度
参数：
	duration：滑动操作持续的时间
用法：
	self.swipe_left()
		'''
		start = (self.device_width-10,self.device_height/2)
		end = (10,self.device_height/2)
		self.swipe(start,end,duration)

	def swipe_right(self,duration=None):
		'''[方法]
swipe_right(duration=None)
从屏幕中间向右划半个屏幕宽度
参数：
	duration：滑动操作持续的时间
用法：
	self.swipe_right()
		'''
		start = (10,self.device_height/2)
		end = (self.device_width-10,self.device_height/2)
		self.swipe(start,end,duration)

	def flick(self, begin, end):
		"""[方法]
flick(begin, end)
Flick from one point to another point.
Args:
	start_x	x-coordinate at which to start
	start_y	y-coordinate at which to start
	end_x	x-coordinate at which to stop
	end_y	y-coordinate at which to stop
:Usage:
	driver.flick(100, 100, 100, 400)
		"""
		if self.autoAcceptAlert:
			self.allow_alert()
		self.logger.log("[action]flick(begin=%s,end=%s)" %(begin,end))
		start_x,start_y = begin
		end_x,end_y = end
		action = TouchAction(self)
		action \
			.press(x=start_x, y=start_y) \
			.move_to(x=end_x, y=end_y) \
			.release()
		action.perform()
		return self

	def equals(self,a,b,strip=False):
		'''[方法]
equals(a,b,strip=False)
判断两个对象a,b是否相等
参数：
	strip：如果是字符串对象是否需要进行strip后对比
		'''
		self.logger.log("[check]equals(a='%s',b='%s')" %(a,b))
		if type(a) != type(b):
			raise CheckError("'%s'(%s) is not the same type as '%s'(%s)" %(a,type(a),b,type(b)))
		if isinstance(a, str) and isinstance(b, str) and strip:
			a = a.strip()
			b = b.strip()

		if a == b:
			return True
		else:
			raise CheckError("'%s' does not equals '%s'" %(a,b))

	def allow_alert(self,nocheck=True):
		'''[方法]
allow_alert(nocheck=True)
允许系统授权弹框
参数：
	nocheck：如果该值为True,则没有弹框时忽略错误继续执行
		'''
		self.logger.log("[action]allow_alert(nocheck='%s')" %nocheck)
		pageSource = self.page_source
		for id in self.system_alert_ids:
			if id[0] in pageSource:
				ele = self.find('id',id[0],nocheck=True)
				if ele:
					ele.click()

	def reject_alert(self,nocheck=True):
		'''[方法]
reject_alert(nocheck=True)
拒绝系统授权弹框
参数：
	nocheck：如果该值为True,则没有弹框时忽略错误继续执行
		'''
		self.logger.log("[action]reject_alert(nocheck='%s')" %nocheck)
		pageSource = self.page_source
		for id in self.system_alert_ids:
			if id[1] in pageSource:
				ele = self.find('id',id[1],nocheck=True)
				if ele:
					ele.click()

	def testdatas(self,name):
		'''[方法]
testdatas(name)
通用测试数据
参数：
	name：数据名称
用法：
	self.testdatas("系统内已有的数据名称")
		'''
		data = self.test_datas.get(name)
		if data:
			return data
		else:
			raise CaseError("testdata '%s' undefined,please add first." %name)

	def conflictdatas(self,name):
		'''[方法]
conflictdatas(name)
互斥测试数据
参数：
	name：数据名称
用法：
	self.conflictdatas("系统内已有的数据名称")
		'''
		if name in self.conflict_datas.keys():
			try:
				data = self.conflict_datas[name].pop()
				return data
			except Exception as e:
				raise CaseError("%s:got no more value to be popped(%s)" %(name,str(e)))
		else:
			raise CaseError("conflictdata '%s' undefined,please add first." %name)

	def click_point(self,x,y,duration=None):
		'''[方法]
click_point(x,y,duration=None)
点击屏幕坐标
参数：
	x：屏幕x坐标
	y：屏幕y坐标
	duration：点击操作持续时长，单位毫秒
用法：
	self.click_point(100,100)
		'''
		self.logger.log("[action]click_point(x=%s,y=%s,duration=%s)" %(x,y,duration))
		action = TouchAction(self)
		if duration:
			action.long_press(x=x, y=y, duration=duration).release()
		else:
			action.tap(x=x, y=y)
		action.perform()
		return self

	def goback(self):
		'''[方法]
按返回按钮
用法：
	self.goback()
		'''
		self.press_keycode(4)
		return self

	def gohome(self):
		'''[方法]
按Home按钮
用法：
	self.gohome()
		'''
		self.press_keycode(3)
		return self

	def parseGestures(self,location,size):
		'''[方法]
parseGestures(location,size)
解析手势密码
参数：
	location：元素的位置信息
	size：元素的大小
返回：
	返回解析后生成的9个坐标点，分别对应九宫格上的点
		'''
		start_x,start_y = location['x'],location['y']
		space_x,space_y = size["width"]/3,size["height"]/3
		points = {}
		floor = 0
		num = 0
		for i in range(1,10):
			if i in [4,7]:
				floor += 1
				num = 0
			points[i] = (round(start_x+space_x*(0.5 + num)),round(start_y+space_y*(0.5+floor)))
			num += 1

		return points

	def gestures_password(self,case_element_name,gestures,nocheck=False):
		'''[方法]
gestures_password(case_element_name,gestures,nocheck=False)
处理手势密码
参数：
	case_element_name：系统内已有元素的名称
	gestures：手势密码需要划过的点代表的数字组成的列表(九宫格每个点代表的数字按照从上至下从左往右的顺序用1-9标记)
	nocheck：如果该值为True,找不到元素时忽略错误继续执行
用法：
	self.gestures_password("手势密码九宫格",[1,2,3,5,7,8,9])  -- 写了一个Z字的手势密码
		'''
		elem = self.super_find(case_element_name,nocheck=nocheck)
		if elem:
			points = self.parseGestures(elem.location,elem.size)
			action = TouchAction(self)
			pre_x,pre_y = None,None
			for index,ges in enumerate(gestures):
				x,y = points[ges]
				self.log("point x:%s,y:%s" %(x,y))
				if index == 0:
					action.press(x=x,y=y)
				else:
					action.move_to(x=x-pre_x,y=y-pre_y)
				pre_x,pre_y = x,y

			action.release().perform()
			return self

	def super_click(self,case_element_name,nocheck=False):
		'''[方法]
super_click(case_element_name,nocheck=False)
点击系统内已添加的某个元素
参数：
	case_element_name：系统内已添加的元素名称
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	self.super_click("登录按钮")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			self.click(by,value,desc=case_element_name,nocheck=nocheck)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)

	def super_clicks(self,case_element_names,nocheck=False):
		'''[方法]
super_clicks(case_element_names,nocheck=False)
点击系统内已添加的多个元素
参数：
	case_element_names：系统内已添加的元素名称列表
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	self.super_clicks(["同意授权按钮",登录按钮"])
		'''
		for name in case_element_names:
			self.super_click(name,nocheck=nocheck)

	def super_exists(self,case_element_name):
		'''[方法]
super_exists(case_element_name)
判断是否能找到系统内已添加的某个元素
参数：
	case_element_name：系统内已添加的元素名称
用法：
	isexists = self.super_exists("登录按钮")
		'''
		if self.super_find(case_element_name,nocheck=True):
			return True
		else:
			return False

	def super_find(self,case_element_name,nocheck=False):
		'''[方法]
super_find(case_element_name,nocheck=False)
查找系统内已添加的某个元素
参数：
	case_element_name：系统内已添加的元素名称
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	self.super_find("登录按钮")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.find(by,value,nocheck=nocheck)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)

	def super_finds(self,case_element_name,nocheck=False):
		'''[方法]
super_finds(case_element_name,nocheck=False)
返回与系统内已添加的元素拥有相同属性的元素列表
参数：
	case_element_name：系统内已添加的元素名称
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	elements = self.super_finds("文章列表")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.finds(by,value,nocheck=nocheck)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)

	def exist_text(self,text):
		'''[方法]
exist_text(text)
查找当前页面是否存在含有text的元素
用法：
	self.exist_text("用户名")
		'''
		self.logger.log("[action]exist_text(text='%s')" %text)
		elem = None
		try:
			elem = self.find("name",str(text),nocheck=False)
		except:
			pass
		finally:
			assert elem is not None,"当前页面未找到文本为'%s'的元素" %text

	def exist_texts(self,texts):
		'''[方法]
exist_texts(texts)
查找当前页面是否存在含有text的元素
用法：
	self.exist_texts(["用户名","密码"])
		'''
		for text in texts:
			self.exist_text(text)

	def super_input(self,case_element_name,text,nocheck=False):
		'''[方法]
super_input(case_element_name,text,nocheck=False)
向系统内已添加的某个元素输入内容
参数：
	case_element_name：系统内已添加的元素名称
	text：需要输入的文字内容
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	self.super_input("用户名输入框","chao.chen")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			self.input(by,value,text,desc=case_element_name,nocheck=nocheck)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)

	def super_inputs(self,case_element_names,text,nocheck=False):
		'''[方法]
super_inputs(case_element_names,text,nocheck=False)
向系统内已添加的多个元素输入内容
参数：
	case_element_names：系统内已添加的元素名称列表
	text：需要输入的文字内容
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	self.super_inputs(["用户名输入框","密码输入框"],"chao.chen")
		'''
		for name in case_element_names:
			self.super_input(name,text,nocheck=nocheck)

	def super_gettext(self,case_element_name,nocheck=False):
		'''[方法]
super_gettext(case_element_name,nocheck=False)
获取某个元素的文本内容
参数：
	case_element_name：系统内已添加的元素名称
	nocheck：该值为True时，找不到元素会忽略错误继续执行
用法：
	text = self.super_gettext("登录按钮")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.gettext(by,value,desc=case_element_name,nocheck=nocheck)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)

	def super_waitfor(self,case_element_name,timeout=10):
		'''[方法]
super_waitfor(case_element_name,timeout=10)
等待某个元素出现
参数：
	case_element_name：系统内已添加的元素名称
	timeout：超时时间
用法：
	self.super_waitfor("登录按钮")
		'''
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.waitfor(by,value,desc=case_element_name,timeout=timeout)
		else:
			error = "系统内未保存名称为'%s'的元素" %case_element_name
			raise CaseError(error)


#=============================================自定义方法  END ==============================================================
	@property
	def contexts(self):
		"""
Returns the contexts within the current session.
:Usage:
	driver.contexts
		"""
		return self.execute(Command.CONTEXTS)['value']

	@property
	def current_context(self):
		"""
Returns the current context of the current session.
:Usage:
	driver.current_context
		"""
		return self.execute(Command.GET_CURRENT_CONTEXT)['value']

	@property
	def context(self):
		"""
Returns the current context of the current session.
:Usage:
	driver.context
		"""
		return self.current_context

	def find_element_by_ios_uiautomation(self, uia_string):
		"""
find_element_by_ios_uiautomation(uia_string)
Finds an element by uiautomation in iOS.
Args:
	uia_string	The element name in the iOS UIAutomation library
:Usage:
	driver.find_element_by_ios_uiautomation('.elements()[1].cells()[2]')
		"""
		return self.find_element(by=By.IOS_UIAUTOMATION, value=uia_string)

	def find_elements_by_ios_uiautomation(self, uia_string):
		"""
find_elements_by_ios_uiautomation(uia_string)
Finds elements by uiautomation in iOS.
Args:
	uia_string	The element name in the iOS UIAutomation library
:Usage:
	driver.find_elements_by_ios_uiautomation('.elements()[1].cells()[2]')
		"""
		return self.find_elements(by=By.IOS_UIAUTOMATION, value=uia_string)

	def find_element_by_android_uiautomator(self, uia_string):
		"""
find_element_by_android_uiautomator(uia_string)
Finds element by uiautomator in Android.
Args:
	uia_string	The element name in the Android UIAutomator library
:Usage:
	driver.find_element_by_android_uiautomator('.elements()[1].cells()[2]')
		"""
		return self.find_element(by=By.ANDROID_UIAUTOMATOR, value=uia_string)

	def find_elements_by_android_uiautomator(self, uia_string):
		"""
find_elements_by_android_uiautomator(uia_string)
Finds elements by uiautomator in Android.
Args:
	uia_string	The element name in the Android UIAutomator library
:Usage:
	driver.find_elements_by_android_uiautomator('.elements()[1].cells()[2]')
		"""
		return self.find_elements(by=By.ANDROID_UIAUTOMATOR, value=uia_string)

	def find_element_by_accessibility_id(self, id):
		"""
find_element_by_accessibility_id(id)
Finds an element by accessibility id.
Args:
	id	a string corresponding to a recursive element search using the
 Id/Name that the native Accessibility options utilize
:Usage:
	driver.find_element_by_accessibility_id()
		"""
		return self.find_element(by=By.ACCESSIBILITY_ID, value=id)

	def find_elements_by_accessibility_id(self, id):
		"""
find_elements_by_accessibility_id(id)
Finds elements by accessibility id.
Args:
	id	a string corresponding to a recursive element search using the
 Id/Name that the native Accessibility options utilize
:Usage:
	driver.find_elements_by_accessibility_id()
		"""
		return self.find_elements(by=By.ACCESSIBILITY_ID, value=id)

	def create_web_element(self, element_id):
		"""
create_web_element(element_id)
Creates a web element with the specified element_id.
Overrides method in Selenium WebDriver in order to always give them
Appium WebElement
		"""
		return MobileWebElement(self, element_id)

	def scroll(self, origin_el, destination_el):
		"""
scroll(origin_el, destination_el)
Scrolls from one element to another
Args:
	originalEl	the element from which to being scrolling
	destinationEl	the element to scroll to
:Usage:
	driver.scroll(el1, el2)
		"""
		self.logger.log("[action]scroll(origin_el='%s',destination_el='%s')" %(origin_el,destination_el))
		action = TouchAction(self)
		action.press(origin_el).move_to(destination_el).release().perform()
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def drag_and_drop(self, origin_el, destination_el):
		"""
drag_and_drop(origin_el, destination_el)
Drag the origin element to the destination element
Args:
	originEl	the element to drag
	destinationEl	the element to drag to
		"""
		self.logger.log("[action]drag_and_drop(origin_el='%s',destination_el='%s')" %(origin_el,destination_el))
		action = TouchAction(self)
		action.long_press(origin_el).move_to(destination_el).release().perform()
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def tap(self, positions, duration=None):
		"""
tap(positions, duration=None)
Taps on an particular place with up to five fingers, holding for a
certain time
Args:
	positions	an array of tuples representing the x/y coordinates of
 the fingers to tap. Length can be up to five.
	duration	(optional) length of time to tap, in ms
:Usage:
	driver.tap([(100, 20), (100, 60), (100, 100)], 500)
		"""
		self.logger.log("[action]tap(positions=%s,destination_el=%s)" %(positions,duration))
		if len(positions) == 1:
			action = TouchAction(self)
			x = positions[0][0]
			y = positions[0][1]
			if duration:
				action.long_press(x=x, y=y, duration=duration).release()
			else:
				action.tap(x=x, y=y)
			action.perform()
		else:
			ma = MultiAction(self)
			for position in positions:
				x = position[0]
				y = position[1]
				action = TouchAction(self)
				if duration:
					action.long_press(x=x, y=y, duration=duration).release()
				else:
					action.press(x=x, y=y).release()
				ma.add(action)

			ma.perform()
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def pinch(self, element=None, percent=200, steps=50):
		"""
pinch(element=None, percent=200, steps=50)
Pinch on an element a certain amount
Args:
	element	the element to pinch
	percent	(optional) amount to pinch. Defaults to 200%
	steps	(optional) number of steps in the pinch action
:Usage:
	driver.pinch(element)
		"""
		self.logger.log("[action]pinck(element='%s',percent=%s,steps=%s)" %(element,percent,steps))
		if element:
			element = element.id

		opts = {
			'element': element,
			'percent': percent,
			'steps': steps,
		}
		self.execute_script('mobile: pinchClose', opts)
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def zoom(self, element=None, percent=200, steps=50):
		"""
zoom(element=None, percent=200, steps=50)
Zooms in on an element a certain amount
Args:
	element	the element to zoom
	percent	(optional) amount to zoom. Defaults to 200%
	steps	(optional) number of steps in the zoom action
:Usage:
	driver.zoom(element)
		"""
		self.logger.log("[action]zoom(element='%s',percent=%s,steps=%s)" %(element,percent,steps))
		if element:
			element = element.id

		opts = {
			'element': element,
			'percent': percent,
			'steps': steps,
		}
		self.execute_script('mobile: pinchOpen', opts)
		return self

	def app_strings(self, language=None, string_file=None):
		"""
app_strings(language=None, string_file=None)
Returns the application strings from the device for the specified
language.
Args:
	language	strings language code
	string_file	the name of the string file to query
		"""
		data = {}
		if language != None:
			data['language'] = language
		if string_file != None:
			data['stringFile'] = string_file
		return self.execute(Command.GET_APP_STRINGS, data)['value']

	def reset(self):
		"""
reset()
Resets the current application on the device.
Usage:
	self.reset()
		"""
		self.logger.log("[action]reset()")
		self.execute(Command.RESET)
		return self

	def hide_keyboard(self, key_name=None, key=None, strategy=None):
		"""
hide_keyboard(key_name=None, key=None, strategy=None)
Hides the software keyboard on the device. In iOS, use `key_name` to press
a particular key, or `strategy`. In Android, no parameters are used.
Args:
	key_name	key to press
	strategy	strategy for closing the keyboard (e.g., `tapOutside`)
		"""
		self.logger.log("[action]hide_keyboard(key_name='%s',key='%s',strategy='%s')" %(key_name,key,strategy))
		data = {}
		if key_name is not None:
			data['keyName'] = key_name
		elif key is not None:
			data['key'] = key
		else:
			# defaults to `tapOutside` strategy
			strategy = 'tapOutside'
		data['strategy'] = strategy
		self.execute(Command.HIDE_KEYBOARD, data)
		return self

	# Needed for Selendroid
	def keyevent(self, keycode, metastate=None):
		"""
keyevent(keycode, metastate=None)
Sends a keycode to the device. Android only. Possible keycodes can be
found in http://developer.android.com/reference/android/view/KeyEvent.html.
Args:
	keycode	the keycode to be sent to the device
	metastate	meta information about the keycode being sent
		"""
		self.logger.log("[action]keyevent(keycode='%s',metastate='%s')" %(keycode,metastate))
		data = {
			'keycode': keycode,
		}
		if metastate is not None:
			data['metastate'] = metastate
		self.execute(Command.KEY_EVENT, data)
		return self

	def press_keycode(self, keycode, metastate=None):
		"""
press_keycode(keycode, metastate=None)
Sends a keycode to the device. Android only. Possible keycodes can be
found in http://developer.android.com/reference/android/view/KeyEvent.html.
Args:
	keycode	the keycode to be sent to the device
	metastate	meta information about the keycode being sent
		"""
		self.logger.log("[action]press_keycode(keycode='%s',metastate='%s')" %(keycode,metastate))
		data = {
			'keycode': keycode,
		}
		if metastate is not None:
			data['metastate'] = metastate
		self.execute(Command.PRESS_KEYCODE, data)
		return self

	def long_press_keycode(self, keycode, metastate=None):
		"""
long_press_keycode(keycode, metastate=None)
Sends a long press of keycode to the device. Android only. Possible keycodes can be
found in http://developer.android.com/reference/android/view/KeyEvent.html.
Args:
	keycode	the keycode to be sent to the device
	metastate	meta information about the keycode being sent
		"""
		self.logger.log("[action]long_press_keycode(keycode='%s',metastate='%s')" %(keycode,metastate))
		data = {
			'keycode': keycode
		}
		if metastate != None:
			data['metastate'] = metastate
		self.execute(Command.LONG_PRESS_KEYCODE, data)
		return self

	@property
	def current_activity(self):
		"""
current_activity()
Retrieves the current activity on the device.
Usage:
	self.current_activity()
		"""
		return self.execute(Command.GET_CURRENT_ACTIVITY)['value']

	def wait_activity(self, activity, timeout, interval=1):
		"""
wait_activity(activity, timeout, interval=1)
Wait for an activity: block until target activity presents
or time out.
This is an Android-only method.
:Agrs:
	activity	target activity
	timeout	max wait time, in seconds
	interval	sleep interval between retries, in seconds
		"""
		self.logger.log("[action]wait_activity(activity='%s',timeout='%s',interval='%s')" %(activity,timeout,interval))
		try:
			WebDriverWait(self, timeout, interval).until(
				lambda d: d.current_activity == activity)
			return True
		except TimeoutException:
			return False

	def set_value(self, element, value):
		"""
set_value(element, value)
Set the value on an element in the application.
Args:
	element	the element whose value will be set
	Value	the value to set on the element
		"""
		self.logger.log("[action]set_value(element='%s',value='%s')" %(element,value))
		data = {
			'elementId': element.id,
			'value': [value],
		}
		self.execute(Command.SET_IMMEDIATE_VALUE, data)
		return self

	def pull_file(self, path):
		"""
pull_file(path)
Retrieves the file at `path`. Returns the file's content encoded as
Base64.
Args:
	path	the path to the file on the device
		"""
		self.logger.log("[action]pull_file(path='%s')" %path)
		data = {
			'path': path,
		}
		return self.execute(Command.PULL_FILE, data)['value']

	def pull_folder(self, path):
		"""
pull_folder(path)
Retrieves a folder at `path`. Returns the folder's contents zipped
and encoded as Base64.
Args:
	path	the path to the folder on the device
		"""
		self.logger.log("[action]pull_folder(path='%s')" %path)
		data = {
			'path': path,
		}
		return self.execute(Command.PULL_FOLDER, data)['value']

	def push_file(self, path, base64data):
		"""
push_file(path, base64data)
Puts the data, encoded as Base64, in the file specified as `path`.
Args:
	path	the path on the device
	base64data	data, encoded as Base64, to be written to the file
		"""
		self.logger.log("[action]push_file(path='%s',base64data='%s')" %(path,base64data))
		data = {
			'path': path,
			'data': base64data,
		}
		self.execute(Command.PUSH_FILE, data)
		return self

	def background_app(self, seconds):
		"""
background_app(seconds)
Puts the application in the background on the device for a certain
duration.
Args:
	seconds	the duration for the application to remain in the background
		"""
		self.logger.log("[action]background_app(seconds=%s)" %seconds)
		data = {
			'seconds': seconds,
		}
		self.execute(Command.BACKGROUND, data)
		return self

	def is_app_installed(self, bundle_id):
		"""
is_app_installed(bundle_id)
Checks whether the application specified by `bundle_id` is installed
on the device.
Args:
	bundle_id	the id of the application to query
		"""
		data = {
			'bundleId': bundle_id,
		}
		return self.execute(Command.IS_APP_INSTALLED, data)['value']

	def install_app(self, app_path):
		"""
install_app(app_path)
Install the application found at `app_path` on the device.
Args:
	app_path	the local or remote path to the application to install
		"""
		self.logger.log("[action]install_app(app_path='%s')" %app_path)
		data = {
			'appPath': app_path,
		}
		self.execute(Command.INSTALL_APP, data)
		return self

	def remove_app(self, app_id):
		"""
remove_app(app_packageName)
Remove the specified application from the device.
Args:
	app_packageName	the application id to be removed
		"""
		self.logger.log("[action]remove_app(appid='%s')" %app_id)
		data = {
			'appId': app_id,
		}
		self.execute(Command.REMOVE_APP, data)
		return self

	def launch_app(self):
		"""
launch_app()
Start on the device the application specified in the desired capabilities.
		"""
		self.logger.log("[action]launch_app()")
		self.execute(Command.LAUNCH_APP)
		return self

	def close_app(self):
		"""
close_app()
Stop the running application, specified in the desired capabilities, on
the device.
		"""
		self.logger.log("[action]close_app()")
		self.execute(Command.CLOSE_APP)
		return self

	def start_activity(self, app_package, app_activity, **opts):
		"""
start_activity(app_package, app_activity, **opts)
Opens an arbitrary activity during a test. If the activity belongs to
another application, that application is started and the activity is opened.
This is an Android-only method.
Args:
- app_package	The package containing the activity to start.
- app_activity	The activity to start.
- app_wait_package	Begin automation after this package starts (optional).
- app_wait_activity	Begin automation after this activity starts (optional).
- intent_action	Intent to start (optional).
- intent_category	Intent category to start (optional).
- intent_flags	Flags to send to the intent (optional).
- optional_intent_arguments	Optional arguments to the intent (optional).
- stop_app_on_reset	Should the app be stopped on reset (optional)?
		"""
		self.logger.log("[action]start_activity(app_package='%s',app_activity='%s',others=%s)" %(app_package,app_activity,opts))
		data = {
			'appPackage': app_package,
			'appActivity': app_activity
		}
		arguments = {
			'app_wait_package': 'appWaitPackage',
			'app_wait_activity': 'appWaitActivity',
			'intent_action': 'intentAction',
			'intent_category': 'intentCategory',
			'intent_flags': 'intentFlags',
			'optional_intent_arguments': 'optionalIntentArguments',
			'stop_app_on_reset': 'stopAppOnReset'
		}
		for key, value in arguments.items():
			if key in opts:
				data[value] = opts[key]
		self.execute(Command.START_ACTIVITY, data)
		return self

	def end_test_coverage(self, intent, path):
		"""
end_test_coverage(intent, path)
Ends the coverage collection and pull the coverage.ec file from the device.
Android only.
See https://github.com/appium/appium/blob/master/docs/en/android_coverage.md
Args:
	intent	description of operation to be performed
	path	path to coverage.ec file to be pulled from the device
		"""
		self.logger.log("[action]end_test_coverage(intent='%s',path='%s')" %(intent,path))
		data = {
			'intent': intent,
			'path': path,
		}
		return self.execute(Command.END_TEST_COVERAGE, data)['value']

	def lock(self, seconds):
		"""
lock(seconds)
Lock the device for a certain period of time. iOS only.
Args:
	the duration to lock the device, in seconds
		"""
		self.logger.log("[action]lock(seconds=%s)" %seconds)
		data = {
			'seconds': seconds,
		}
		self.execute(Command.LOCK, data)
		return self

	def shake(self):
		"""
shake()
Shake the device.
		"""
		self.logger.log("[action]lock()")
		self.execute(Command.SHAKE)
		return self

	def open_notifications(self):
		"""
open_notifications()
Open notification shade in Android (API Level 18 and above)
		"""
		self.logger.log("[action]open_notifications()")
		self.execute(Command.OPEN_NOTIFICATIONS, {})
		return self

	@property
	def network_connection(self):
		"""
Returns an integer bitmask specifying the network connection type.
Android only.
Possible values are available through the enumeration `appium.webdriver.ConnectionType`
		"""
		return self.execute(Command.GET_NETWORK_CONNECTION, {})['value']

	def set_network_connection(self, connectionType):
		"""
set_network_connection(connectionType)
Sets the network connection type. Android only.
Possible values:
	Value (Alias)	  | Data | Wifi | Airplane Mode
	-------------------------------------------------
	0 (None)		   | 0	| 0	| 0
	1 (Airplane Mode)  | 0	| 0	| 1
	2 (Wifi only)	  | 0	| 1	| 0
	4 (Data only)	  | 1	| 0	| 0
	6 (All network on) | 1	| 1	| 0
These are available through the enumeration `appium.webdriver.ConnectionType`
Args:
	connectionType	a member of the enum appium.webdriver.ConnectionType
		"""
		self.logger.log("[action]set_network_connection(connectionType='%s')" %connectionType)
		data = {
			'parameters': {
				'type': connectionType
			}
		}
		return self.execute(Command.SET_NETWORK_CONNECTION, data)['value']

	@property
	def available_ime_engines(self):
		"""
available_ime_engines -property
Get the available input methods for an Android device. Package and
activity are returned (e.g., ['com.android.inputmethod.latin/.LatinIME'])
Android only.
		"""
		return self.execute(Command.GET_AVAILABLE_IME_ENGINES, {})['value']

	def is_ime_active(self):
		"""
is_ime_active()
Checks whether the device has IME service active. Returns True/False.
Android only.
		"""
		return self.execute(Command.IS_IME_ACTIVE, {})['value']

	def activate_ime_engine(self, engine):
		"""
activate_ime_engine(engine)
Activates the given IME engine on the device.
Android only.
Args:
	engine	the package and activity of the IME engine to activate (e.g.,
	'com.android.inputmethod.latin/.LatinIME')
		"""
		self.logger.log("[action]activate_ime_engine(engine='%s')" %engine)
		data = {
			'engine': engine
		}
		self.execute(Command.ACTIVATE_IME_ENGINE, data)
		return self

	def deactivate_ime_engine(self):
		"""
deactivate_ime_engine()
Deactivates the currently active IME engine on the device.
Android only.
		"""
		self.logger.log("[action]deactivate_ime_engine()")
		self.execute(Command.DEACTIVATE_IME_ENGINE, {})
		return self

	@property
	def active_ime_engine(self):
		"""
active_ime_engine  -property
Returns the activity and package of the currently active IME engine (e.g.,
'com.android.inputmethod.latin/.LatinIME').
Android only.
		"""
		return self.execute(Command.GET_ACTIVE_IME_ENGINE, {})['value']

	def get_settings(self):
		"""
get_settings()
Returns the appium server Settings for the current session.
Do not get Settings confused with Desired Capabilities, they are
separate concepts. See https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
		"""
		self.logger.log("[action]get_settings()")
		return self.execute(Command.GET_SETTINGS, {})['value']

	def update_settings(self, settings):
		"""
update_settings(settings)
Set settings for the current session.
For more on settings, see: https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
Args:
	settings	dictionary of settings to apply to the current test session
		"""
		self.logger.log("[action]update_settings(settings=%s)" %settings)
		data = {"settings": settings}

		self.execute(Command.UPDATE_SETTINGS, data)
		return self

	def toggle_location_services(self):
		"""
toggle_location_services()
Toggle the location services on the device. Android only.
		"""
		self.logger.log("[action]toggle_location_services()")
		self.execute(Command.TOGGLE_LOCATION_SERVICES, {})
		return self

	def set_location(self, latitude, longitude, altitude):
		"""
set_location(latitude, longitude, altitude)
Set the location of the device
Args:
	latitude	String or numeric value between -90.0 and 90.00
	longitude	String or numeric value between -180.0 and 180.0
	altitude	String or numeric value
		"""
		self.logger.log("[action]set_location(latitude=%s,longitude=%s,altitude=%s)" %(latitude,longitude,altitude))
		data = {
			"location": {
				"latitude": str(latitude),
				"longitude": str(longitude),
				"altitude": str(altitude)
			}
		}
		self.execute(Command.SET_LOCATION, data)
		return self

	def _addCommands(self):
		self.command_executor._commands[Command.CONTEXTS] = \
			('GET', '/session/$sessionId/contexts')
		self.command_executor._commands[Command.GET_CURRENT_CONTEXT] = \
			('GET', '/session/$sessionId/context')
		self.command_executor._commands[Command.SWITCH_TO_CONTEXT] = \
			('POST', '/session/$sessionId/context')
		self.command_executor._commands[Command.TOUCH_ACTION] = \
			('POST', '/session/$sessionId/touch/perform')
		self.command_executor._commands[Command.MULTI_ACTION] = \
			('POST', '/session/$sessionId/touch/multi/perform')
		self.command_executor._commands[Command.GET_APP_STRINGS] = \
			('POST', '/session/$sessionId/appium/app/strings')
		# Needed for Selendroid
		self.command_executor._commands[Command.KEY_EVENT] = \
			('POST', '/session/$sessionId/appium/device/keyevent')
		self.command_executor._commands[Command.PRESS_KEYCODE] = \
			('POST', '/session/$sessionId/appium/device/press_keycode')
		self.command_executor._commands[Command.LONG_PRESS_KEYCODE] = \
			('POST', '/session/$sessionId/appium/device/long_press_keycode')
		self.command_executor._commands[Command.GET_CURRENT_ACTIVITY] = \
			('GET', '/session/$sessionId/appium/device/current_activity')
		self.command_executor._commands[Command.SET_IMMEDIATE_VALUE] = \
			('POST', '/session/$sessionId/appium/element/$elementId/value')
		self.command_executor._commands[Command.PULL_FILE] = \
			('POST', '/session/$sessionId/appium/device/pull_file')
		self.command_executor._commands[Command.PULL_FOLDER] = \
			('POST', '/session/$sessionId/appium/device/pull_folder')
		self.command_executor._commands[Command.PUSH_FILE] = \
			('POST', '/session/$sessionId/appium/device/push_file')
		self.command_executor._commands[Command.BACKGROUND] = \
			('POST', '/session/$sessionId/appium/app/background')
		self.command_executor._commands[Command.IS_APP_INSTALLED] = \
			('POST', '/session/$sessionId/appium/device/app_installed')
		self.command_executor._commands[Command.INSTALL_APP] = \
			('POST', '/session/$sessionId/appium/device/install_app')
		self.command_executor._commands[Command.REMOVE_APP] = \
			('POST', '/session/$sessionId/appium/device/remove_app')
		self.command_executor._commands[Command.START_ACTIVITY] = \
			('POST', '/session/$sessionId/appium/device/start_activity')
		self.command_executor._commands[Command.LAUNCH_APP] = \
			('POST', '/session/$sessionId/appium/app/launch')
		self.command_executor._commands[Command.CLOSE_APP] = \
			('POST', '/session/$sessionId/appium/app/close')
		self.command_executor._commands[Command.END_TEST_COVERAGE] = \
			('POST', '/session/$sessionId/appium/app/end_test_coverage')
		self.command_executor._commands[Command.LOCK] = \
			('POST', '/session/$sessionId/appium/device/lock')
		self.command_executor._commands[Command.SHAKE] = \
			('POST', '/session/$sessionId/appium/device/shake')
		self.command_executor._commands[Command.RESET] = \
			('POST', '/session/$sessionId/appium/app/reset')
		self.command_executor._commands[Command.HIDE_KEYBOARD] = \
			('POST', '/session/$sessionId/appium/device/hide_keyboard')
		self.command_executor._commands[Command.OPEN_NOTIFICATIONS] = \
			('POST', '/session/$sessionId/appium/device/open_notifications')
		self.command_executor._commands[Command.GET_NETWORK_CONNECTION] = \
			('GET', '/session/$sessionId/network_connection')
		self.command_executor._commands[Command.SET_NETWORK_CONNECTION] = \
			('POST', '/session/$sessionId/network_connection')
		self.command_executor._commands[Command.GET_AVAILABLE_IME_ENGINES] = \
			('GET', '/session/$sessionId/ime/available_engines')
		self.command_executor._commands[Command.IS_IME_ACTIVE] = \
			('GET', '/session/$sessionId/ime/activated')
		self.command_executor._commands[Command.ACTIVATE_IME_ENGINE] = \
			('POST', '/session/$sessionId/ime/activate')
		self.command_executor._commands[Command.DEACTIVATE_IME_ENGINE] = \
			('POST', '/session/$sessionId/ime/deactivate')
		self.command_executor._commands[Command.GET_ACTIVE_IME_ENGINE] = \
			('GET', '/session/$sessionId/ime/active_engine')
		self.command_executor._commands[Command.REPLACE_KEYS] = \
			('POST', '/session/$sessionId/appium/element/$id/replace_value')
		self.command_executor._commands[Command.GET_SETTINGS] = \
			('GET', '/session/$sessionId/appium/settings')
		self.command_executor._commands[Command.UPDATE_SETTINGS] = \
			('POST', '/session/$sessionId/appium/settings')
		self.command_executor._commands[Command.TOGGLE_LOCATION_SERVICES] = \
			('POST', '/session/$sessionId/appium/device/toggle_location_services')
		self.command_executor._commands[Command.SET_LOCATION] = \
			('POST', '/session/$sessionId/location')
		self.command_executor._commands[Command.LOCATION_IN_VIEW] = \
			('GET', '/session/$sessionId/element/$id/location_in_view')