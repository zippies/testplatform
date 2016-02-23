# -*- coding: utf-8 -*-
import os,random

class CaseElements(object):
	def __init__(self,elements):
		self._parseElement(elements)

	def _parseElement(self,elements):

		for element in elements:
			name, by ,value = element.name , element.findby , element.value
			setattr(self,name,(by,value))

	def get(self,name):
		if hasattr(self,name):
			return getattr(self,name)
		else:
			return (None,None)

class TestData(object):
	def __init__(self,testdatas):
		self._parseDatas(testdatas)

	def _parseDatas(self,testdatas):
		for testdata in testdatas:
			name , value = testdata.name , testdata.value
			setattr(self,name,eval(value))

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