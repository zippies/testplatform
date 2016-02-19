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
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import os,time


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
	def sleep(self,seconds):
		self.logger.log("[action]sleep(seconds='%s')" %seconds)
		time.sleep(seconds)

	def find(self,by,value,nocheck=False):
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
		if by not in ['id','accessibility_id','class_name','css_selector','name','link_text','partial_link_text','xpath','ios_uiautomation','android_uiautomator']:
			raise CaseError("'find' function doesn't support such type:'%s'" %by)

		try:
			eles = eval("self.find_elements_by_%s" %by)(value)
			return eles
		except Exception as e:
			if not nocheck:
				raise CaseError("Elements not found using '%s' : %s" %(by,value))
			else:
				return []

	def click(self,by,value,desc="",nocheck=False):
		self.logger.log("[action]click(by='%s',value='%s',nocheck=%s) '%s'" %(by,value,nocheck,desc))
		if not isinstance(value, str):
			raise CaseError("'click' function required a str type on 'value' parameter")

		ele = self.find(by,value,nocheck)
		
		if not ele and nocheck:
			return None
		else:
			ele.click()

	def save_screen(self,filename=None,immediate=False):
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
		self.logger.log("[action]input(by='%s',value='%s',text='%s',nocheck=%s) '%s'" %(by,value,text,nocheck,desc))
		ele = self.find(by,value,nocheck)
		if not ele and nocheck:
			return None
		else:
			ele.send_keys(text)

	def gettext(self,by,value,desc="",nocheck=False):
		self.logger.log("[action]gettext(by='%s',value='%s',nocheck=%s) '%s'" %(by,value,nocheck,desc))
		ele = self.find(by,value,nocheck)

		if not ele and nocheck:
			return None
		else:
			return ele.text

	def waitfor(self,by,value,desc="",timeout=10):
		self.logger.log("[action]waitfor(by='%s',value='%s',timeout=%s) '%s'" %(by,value,timeout,desc))
		try:
			WebDriverWait(self,timeout,1).until(
				lambda x: getattr(x,'find_element_by_%s' %by)(value).is_displayed()
			)
			return self.find(by,value)
		except:
			raise ActionTimeOut("'%s:%s' element not shown after %s seconds '%s'" %(by,value,timeout,desc))

	def swipe(self,begin,end,duration=None):
		"""Swipe from one point to another point, for an optional duration.
		:Args:
		 - start_x - x-coordinate at which to start
		 - start_y - y-coordinate at which to start
		 - end_x - x-coordinate at which to stop
		 - end_y - y-coordinate at which to stop
		 - duration - (optional) time to take the swipe, in ms.
		:Usage:
			driver.swipe((100, 100), (100, 400))
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
		'''
			swipe up full screen height
		'''
		start = (self.device_width/2,self.device_height-10)
		end = (self.device_width/2,10)
		self.swipe(start,end,duration)

	def swipe_down(self,duration=None):
		'''
			swipe down full screen height
		'''
		start = (self.device_width/2,10)
		end = (self.device_width/2,self.device_height-10)
		self.swipe(start,end,duration)

	def swipe_left(self,duration=None):
		'''
			swipe left full screen width
		'''
		start = (self.device_width-10,self.device_height/2)
		end = (10,self.device_height/2)
		self.swipe(start,end,duration)

	def swipe_right(self,duration=None):
		'''
			swipe right full screen width
		'''
		start = (10,self.device_height/2)
		end = (self.device_width-10,self.device_height/2)
		self.swipe(start,end,duration)

	def flick(self, begin, end):
		"""Flick from one point to another point.
		:Args:
		 - start_x - x-coordinate at which to start
		 - start_y - y-coordinate at which to start
		 - end_x - x-coordinate at which to stop
		 - end_y - y-coordinate at which to stop
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
		pageSource = self.page_source
		for id in self.system_alert_ids:
			if id[0] in pageSource:
				ele = self.find('id',id[0],nocheck=True)
				if ele:
					ele.click()

	def reject_alert(self,nocheck=True):
		pageSource = self.page_source
		for id in self.system_alert_ids:
			if id[1] in pageSource:
				ele = self.find('id',id[1],nocheck=True)
				if ele:
					ele.click()

	def get_conflict(self,name):
		if name in self.conflict_datas.keys():
			try:
				data = self.conflict_datas[name].pop()
				return data
			except Exception as e:
				raise CaseError("%s:got no more value to be popped(%s)" %(name,str(e)))
		else:
			raise CaseError("undefined:%s check your 'androidConfig.py' to see if it is configured correctly" %name)

	def click_point(self,x,y,duration=None):
		self.logger.log("[action]click_point(x=%s,y=%s,duration=%s)" %(x,y,duration))
		action = TouchAction(self)
		if duration:
			action.long_press(x=x, y=y, duration=duration).release()
		else:
			action.tap(x=x, y=y)
		action.perform()
		return self

	def goback(self):
		self.press_keycode(4)
		return self

	def gohome(self):
		self.press_keycode(3)
		return self

	def parseGestures(self,location,size):
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

	def deal_gestures_password(self,case_element_name,gestures,nocheck=False):
		elem = self.super_find(case_element_name,nocheck=nocheck)
		points = self.parseGestures(elem.location,elem.size)
		action = TouchAction(self)
		for index,ges in enumerate(gestures):
			x,y = points[ges]
			if index == 0:
				action = action.long_press(x=x,y=y)
			else:
				action = action.move_to(x=x,y=y)

		action.release().perform()
		return self

	def super_click(self,case_element_name,nocheck=False):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			self.click(by,value,desc=case_element_name,nocheck=nocheck)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
			raise CaseError(error)

	def super_clicks(self,case_element_names,nocheck=False):
		for name in case_element_names:
			self.super_click(name,nocheck=nocheck)

	def super_exists(self,case_element_name):
		if self.super_find(case_element_name,nocheck=True):
			return True
		else:
			return False

	def super_find(self,case_element_name,nocheck=False):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.find(by,value,nocheck=nocheck)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
			raise CaseError(error)

	def super_finds(self,case_element_name,nocheck=False):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.finds(by,value,nocheck=nocheck)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
			raise CaseError(error)

	def super_input(self,case_element_name,text,nocheck=False):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			self.input(by,value,text,desc=case_element_name,nocheck=nocheck)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
			raise CaseError(error)

	def super_inputs(self,case_element_names,text,nocheck=False):
		for name in case_element_names:
			self.super_input(name,text,nocheck=nocheck)

	def super_gettext(self,case_element_name,nocheck=False):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.gettext(by,value,desc=case_element_name,nocheck=nocheck)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
			raise CaseError(error)

	def super_waitfor(self,case_element_name,timeout=10):
		by,value = self.case_elements.get(case_element_name)
		if by and value:
			return self.waitfor(by,value,desc=case_element_name,timeout=timeout)
		else:
			error = "'element:%s' is not configured in '%s'" %(case_element_name,self.case_elements.elementfile or 'androidConfig.py')
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
		"""Finds an element by uiautomation in iOS.
		:Args:
		 - uia_string - The element name in the iOS UIAutomation library
		:Usage:
			driver.find_element_by_ios_uiautomation('.elements()[1].cells()[2]')
		"""
		return self.find_element(by=By.IOS_UIAUTOMATION, value=uia_string)

	def find_elements_by_ios_uiautomation(self, uia_string):
		"""Finds elements by uiautomation in iOS.
		:Args:
		 - uia_string - The element name in the iOS UIAutomation library
		:Usage:
			driver.find_elements_by_ios_uiautomation('.elements()[1].cells()[2]')
		"""
		return self.find_elements(by=By.IOS_UIAUTOMATION, value=uia_string)

	def find_element_by_android_uiautomator(self, uia_string):
		"""Finds element by uiautomator in Android.
		:Args:
		 - uia_string - The element name in the Android UIAutomator library
		:Usage:
			driver.find_element_by_android_uiautomator('.elements()[1].cells()[2]')
		"""
		return self.find_element(by=By.ANDROID_UIAUTOMATOR, value=uia_string)

	def find_elements_by_android_uiautomator(self, uia_string):
		"""Finds elements by uiautomator in Android.
		:Args:
		 - uia_string - The element name in the Android UIAutomator library
		:Usage:
			driver.find_elements_by_android_uiautomator('.elements()[1].cells()[2]')
		"""
		return self.find_elements(by=By.ANDROID_UIAUTOMATOR, value=uia_string)

	def find_element_by_accessibility_id(self, id):
		"""Finds an element by accessibility id.
		:Args:
		 - id - a string corresponding to a recursive element search using the
		 Id/Name that the native Accessibility options utilize
		:Usage:
			driver.find_element_by_accessibility_id()
		"""
		return self.find_element(by=By.ACCESSIBILITY_ID, value=id)

	def find_elements_by_accessibility_id(self, id):
		"""Finds elements by accessibility id.
		:Args:
		 - id - a string corresponding to a recursive element search using the
		 Id/Name that the native Accessibility options utilize
		:Usage:
			driver.find_elements_by_accessibility_id()
		"""
		return self.find_elements(by=By.ACCESSIBILITY_ID, value=id)

	def create_web_element(self, element_id):
		"""
		Creates a web element with the specified element_id.
		Overrides method in Selenium WebDriver in order to always give them
		Appium WebElement
		"""
		#self.logger.log("[action]create_web_element(element_id='%s')" %element_id)
		return MobileWebElement(self, element_id)

	def scroll(self, origin_el, destination_el):
		"""Scrolls from one element to another
		:Args:
		 - originalEl - the element from which to being scrolling
		 - destinationEl - the element to scroll to
		:Usage:
			driver.scroll(el1, el2)
		"""
		self.logger.log("[action]scroll(origin_el='%s',destination_el='%s')" %(origin_el,destination_el))
		action = TouchAction(self)
		action.press(origin_el).move_to(destination_el).release().perform()
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def drag_and_drop(self, origin_el, destination_el):
		"""Drag the origin element to the destination element
		:Args:
		 - originEl - the element to drag
		 - destinationEl - the element to drag to
		"""
		self.logger.log("[action]drag_and_drop(origin_el='%s',destination_el='%s')" %(origin_el,destination_el))
		action = TouchAction(self)
		action.long_press(origin_el).move_to(destination_el).release().perform()
		return self

	# convenience method added to Appium (NOT Selenium 3)
	def tap(self, positions, duration=None):
		"""Taps on an particular place with up to five fingers, holding for a
		certain time
		:Args:
		 - positions - an array of tuples representing the x/y coordinates of
		 the fingers to tap. Length can be up to five.
		 - duration - (optional) length of time to tap, in ms
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
		"""Pinch on an element a certain amount
		:Args:
		 - element - the element to pinch
		 - percent - (optional) amount to pinch. Defaults to 200%
		 - steps - (optional) number of steps in the pinch action
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
		"""Zooms in on an element a certain amount
		:Args:
		 - element - the element to zoom
		 - percent - (optional) amount to zoom. Defaults to 200%
		 - steps - (optional) number of steps in the zoom action
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
		"""Returns the application strings from the device for the specified
		language.
		:Args:
		 - language - strings language code
		 - string_file - the name of the string file to query
		"""
		data = {}
		if language != None:
			data['language'] = language
		if string_file != None:
			data['stringFile'] = string_file
		return self.execute(Command.GET_APP_STRINGS, data)['value']

	def reset(self):
		"""Resets the current application on the device.
		"""
		self.logger.log("[action]reset()")
		self.execute(Command.RESET)
		return self

	def hide_keyboard(self, key_name=None, key=None, strategy=None):
		"""Hides the software keyboard on the device. In iOS, use `key_name` to press
		a particular key, or `strategy`. In Android, no parameters are used.
		:Args:
		 - key_name - key to press
		 - strategy - strategy for closing the keyboard (e.g., `tapOutside`)
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
		"""Sends a keycode to the device. Android only. Possible keycodes can be
		found in http://developer.android.com/reference/android/view/KeyEvent.html.
		:Args:
		 - keycode - the keycode to be sent to the device
		 - metastate - meta information about the keycode being sent
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
		"""Sends a keycode to the device. Android only. Possible keycodes can be
		found in http://developer.android.com/reference/android/view/KeyEvent.html.
		:Args:
		 - keycode - the keycode to be sent to the device
		 - metastate - meta information about the keycode being sent
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
		"""Sends a long press of keycode to the device. Android only. Possible keycodes can be
		found in http://developer.android.com/reference/android/view/KeyEvent.html.
		:Args:
		 - keycode - the keycode to be sent to the device
		 - metastate - meta information about the keycode being sent
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
		"""Retrieves the current activity on the device.
		"""
		return self.execute(Command.GET_CURRENT_ACTIVITY)['value']

	def wait_activity(self, activity, timeout, interval=1):
		"""Wait for an activity: block until target activity presents
		or time out.
		This is an Android-only method.
		:Agrs:
		 - activity - target activity
		 - timeout - max wait time, in seconds
		 - interval - sleep interval between retries, in seconds
		"""
		self.logger.log("[action]wait_activity(activity='%s',timeout='%s',interval='%s')" %(activity,timeout,interval))
		try:
			WebDriverWait(self, timeout, interval).until(
				lambda d: d.current_activity == activity)
			return True
		except TimeoutException:
			return False

	def set_value(self, element, value):
		"""Set the value on an element in the application.
		:Args:
		 - element - the element whose value will be set
		 - Value - the value to set on the element
		"""
		self.logger.log("[action]set_value(element='%s',value='%s')" %(element,value))
		data = {
			'elementId': element.id,
			'value': [value],
		}
		self.execute(Command.SET_IMMEDIATE_VALUE, data)
		return self

	def pull_file(self, path):
		"""Retrieves the file at `path`. Returns the file's content encoded as
		Base64.
		:Args:
		 - path - the path to the file on the device
		"""
		self.logger.log("[action]pull_file(path='%s')" %path)
		data = {
			'path': path,
		}
		return self.execute(Command.PULL_FILE, data)['value']

	def pull_folder(self, path):
		"""Retrieves a folder at `path`. Returns the folder's contents zipped
		and encoded as Base64.
		:Args:
		 - path - the path to the folder on the device
		"""
		self.logger.log("[action]pull_folder(path='%s')" %path)
		data = {
			'path': path,
		}
		return self.execute(Command.PULL_FOLDER, data)['value']

	def push_file(self, path, base64data):
		"""Puts the data, encoded as Base64, in the file specified as `path`.
		:Args:
		 - path - the path on the device
		 - base64data - data, encoded as Base64, to be written to the file
		"""
		self.logger.log("[action]push_file(path='%s',base64data='%s')" %(path,base64data))
		data = {
			'path': path,
			'data': base64data,
		}
		self.execute(Command.PUSH_FILE, data)
		return self

	def background_app(self, seconds):
		"""Puts the application in the background on the device for a certain
		duration.
		:Args:
		 - seconds - the duration for the application to remain in the background
		"""
		self.logger.log("[action]background_app(seconds=%s)" %seconds)
		data = {
			'seconds': seconds,
		}
		self.execute(Command.BACKGROUND, data)
		return self

	def is_app_installed(self, bundle_id):
		"""Checks whether the application specified by `bundle_id` is installed
		on the device.
		:Args:
		 - bundle_id - the id of the application to query
		"""
		data = {
			'bundleId': bundle_id,
		}
		return self.execute(Command.IS_APP_INSTALLED, data)['value']

	def install_app(self, app_path):
		"""Install the application found at `app_path` on the device.
		:Args:
		 - app_path - the local or remote path to the application to install
		"""
		self.logger.log("[action]install_app(app_path='%s')" %app_path)
		data = {
			'appPath': app_path,
		}
		self.execute(Command.INSTALL_APP, data)
		return self

	def remove_app(self, app_id):
		"""Remove the specified application from the device.
		:Args:
		 - app_id - the application id to be removed
		"""
		self.logger.log("[action]remove_app(appid='%s')" %app_id)
		data = {
			'appId': app_id,
		}
		self.execute(Command.REMOVE_APP, data)
		return self

	def launch_app(self):
		"""Start on the device the application specified in the desired capabilities.
		"""
		self.logger.log("[action]launch_app()")
		self.execute(Command.LAUNCH_APP)
		return self

	def close_app(self):
		"""Stop the running application, specified in the desired capabilities, on
		the device.
		"""
		self.logger.log("[action]close_app()")
		self.execute(Command.CLOSE_APP)
		return self

	def start_activity(self, app_package, app_activity, **opts):
		"""Opens an arbitrary activity during a test. If the activity belongs to
		another application, that application is started and the activity is opened.
		This is an Android-only method.
		:Args:
		- app_package - The package containing the activity to start.
		- app_activity - The activity to start.
		- app_wait_package - Begin automation after this package starts (optional).
		- app_wait_activity - Begin automation after this activity starts (optional).
		- intent_action - Intent to start (optional).
		- intent_category - Intent category to start (optional).
		- intent_flags - Flags to send to the intent (optional).
		- optional_intent_arguments - Optional arguments to the intent (optional).
		- stop_app_on_reset - Should the app be stopped on reset (optional)?
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
		self.logger.log("[action]end_test_coverage(intent='%s',path='%s')" %(intent,path))
		"""Ends the coverage collection and pull the coverage.ec file from the device.
		Android only.
		See https://github.com/appium/appium/blob/master/docs/en/android_coverage.md
		:Args:
		 - intent - description of operation to be performed
		 - path - path to coverage.ec file to be pulled from the device
		"""
		data = {
			'intent': intent,
			'path': path,
		}
		return self.execute(Command.END_TEST_COVERAGE, data)['value']

	def lock(self, seconds):
		"""Lock the device for a certain period of time. iOS only.
		:Args:
		 - the duration to lock the device, in seconds
		"""
		self.logger.log("[action]lock(seconds=%s)" %seconds)
		data = {
			'seconds': seconds,
		}
		self.execute(Command.LOCK, data)
		return self

	def shake(self):
		"""Shake the device.
		"""
		self.logger.log("[action]lock()")
		self.execute(Command.SHAKE)
		return self

	def open_notifications(self):
		"""Open notification shade in Android (API Level 18 and above)
		"""
		self.logger.log("[action]open_notifications()")
		self.execute(Command.OPEN_NOTIFICATIONS, {})
		return self

	@property
	def network_connection(self):
		"""Returns an integer bitmask specifying the network connection type.
		Android only.
		Possible values are available through the enumeration `appium.webdriver.ConnectionType`
		"""
		return self.execute(Command.GET_NETWORK_CONNECTION, {})['value']

	def set_network_connection(self, connectionType):
		"""Sets the network connection type. Android only.
		Possible values:
			Value (Alias)	  | Data | Wifi | Airplane Mode
			-------------------------------------------------
			0 (None)		   | 0	| 0	| 0
			1 (Airplane Mode)  | 0	| 0	| 1
			2 (Wifi only)	  | 0	| 1	| 0
			4 (Data only)	  | 1	| 0	| 0
			6 (All network on) | 1	| 1	| 0
		These are available through the enumeration `appium.webdriver.ConnectionType`
		:Args:
		 - connectionType - a member of the enum appium.webdriver.ConnectionType
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
		"""Get the available input methods for an Android device. Package and
		activity are returned (e.g., ['com.android.inputmethod.latin/.LatinIME'])
		Android only.
		"""
		return self.execute(Command.GET_AVAILABLE_IME_ENGINES, {})['value']

	def is_ime_active(self):
		"""Checks whether the device has IME service active. Returns True/False.
		Android only.
		"""
		return self.execute(Command.IS_IME_ACTIVE, {})['value']

	def activate_ime_engine(self, engine):
		"""Activates the given IME engine on the device.
		Android only.
		:Args:
		 - engine - the package and activity of the IME engine to activate (e.g.,
			'com.android.inputmethod.latin/.LatinIME')
		"""
		self.logger.log("[action]activate_ime_engine(engine='%s')" %engine)
		data = {
			'engine': engine
		}
		self.execute(Command.ACTIVATE_IME_ENGINE, data)
		return self

	def deactivate_ime_engine(self):
		"""Deactivates the currently active IME engine on the device.
		Android only.
		"""
		self.logger.log("[action]deactivate_ime_engine()")
		self.execute(Command.DEACTIVATE_IME_ENGINE, {})
		return self

	@property
	def active_ime_engine(self):
		"""Returns the activity and package of the currently active IME engine (e.g.,
		'com.android.inputmethod.latin/.LatinIME').
		Android only.
		"""
		return self.execute(Command.GET_ACTIVE_IME_ENGINE, {})['value']

	def get_settings(self):
		"""Returns the appium server Settings for the current session.
		Do not get Settings confused with Desired Capabilities, they are
		separate concepts. See https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
		"""
		self.logger.log("[action]get_settings()")
		return self.execute(Command.GET_SETTINGS, {})['value']

	def update_settings(self, settings):
		"""Set settings for the current session.
		For more on settings, see: https://github.com/appium/appium/blob/master/docs/en/advanced-concepts/settings.md
		:Args:
		 - settings - dictionary of settings to apply to the current test session
		"""
		self.logger.log("[action]update_settings(settings=%s)" %settings)
		data = {"settings": settings}

		self.execute(Command.UPDATE_SETTINGS, data)
		return self

	def toggle_location_services(self):
		"""Toggle the location services on the device. Android only.
		"""
		self.logger.log("[action]toggle_location_services()")
		self.execute(Command.TOGGLE_LOCATION_SERVICES, {})
		return self

	def set_location(self, latitude, longitude, altitude):
		"""Set the location of the device
		:Args:
		 - latitude - String or numeric value between -90.0 and 90.00
		 - longitude - String or numeric value between -180.0 and 180.0
		 - altitude - String or numeric value
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