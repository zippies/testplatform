# -*- coding: utf-8 -*-
import os,random

class CaseElements(object):
	def __init__(self,elements):
		self.elementfile = None
		self._parseElement(elements)

	def _parseElement(self,elements):

		for element in elements:
			name, by ,value = element.name,element.findby,element.value
			setattr(self,name,(by,value))

	def get(self,name):
		if hasattr(self,name):
			return getattr(self,name)
		else:
			return (None,None)

class TestData(object):
	def __init__(self,datastr):
		self.testdatafile = datastr
		self._parseDatas(datastr)

	def _parseDatas(self,datastr):
		if os.path.exists(datastr):
			with open(element_str,'r') as f:
				self.datafile = datastr
				datastr = f.read().strip()

		lines = [line for line in datastr.split("\n") if line.strip("\t ")]
		for line in lines:
			try:
				name ,value = [s.strip("\t ") for s in line.split('|')]
				setattr(self,name,eval(value))
			except:
				continue

	def get(self,name,special_index=0):
		if hasattr(self,name):
			values = getattr(self,name)
			if isinstance(values, str):
				return values
			elif isinstance(values, list):
				if special_index > len(values):
					return None
				else:
					return values[special_index-1] if special_index else random.sample(values,1)[0]
		else:
			return None

if __name__ == '__main__':
	from pprint import pprint
	#c = CaseElements('C:\\Users\\Administrator\\Desktop\\selftest\\defender\\elements.txt')
	case_elements = \
	'''
	注册登录按钮		|xpath		 	 |LinearLayout/Button
	手机号输入框		|xpath			 |LinearLayout/RelativeLayout/EditText
	下一步输入密码		|xpath	 		 |RelativeLayout/LinearLayout[2]/ImageView
	密码输入框			|xpath			 |LinearLayout/RelativeLayout/EditText
	登录按钮 			|xpath			 |RelativeLayout/LinearLayout[2]/ImageView
	'''
	c = CaseElements(case_elements)
	pprint(dir(c))
	print(c.get("下一步输入密码"))

# if __name__ == '__main__':
# 	datas = \
# 	'''
# 	usernames	|	[ 11266661001, 11266661002, 11266661003]
# 	passwords	|	[ '111111 ' ]
# 	evaluates 	|	[ "good good study,day day up!" ]
# 	'''
# 	c = TestData(datas)
# 	#pprint(dir(c))
# 	print(c.get("usernames"))
# 	print(c.get("passwords"))
# 	print(c.get("evaluates"))