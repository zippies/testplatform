# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify
from ..models import db,Testcase,Appelement
from flask.ext.login import login_required
from .. import Config
from jinja2 import Template
from . import main
import json,os

caselist_template = '''
{% for case in cases %}
<tr>
	<td><input type="checkbox" name="choicedCase" id="case_{{ case.id }}" value={{ case.id }} /></td>
	<td id="casename_{{ case.id }}" class="casename">{{ case.name }}</td>
	<td id="casedesc_{{ case.id }}" class="casedesc">{{ case.desc }}</td>
</tr>
{% endfor %}
'''

case_template = \
'''
# -*- coding: utf-8 -*-
from main.android.basecase import AndroidDevice
{% for lib in libs %}{{lib}};{% endfor %}

class TestCase(AndroidDevice):
	desc = "{{ desc }}"

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
{% for action in actions %}
		{{ action }}
{% endfor %}
'''

@main.route("/getcases")
def getcases():
	global caselist_template
	data = []
	cases = Testcase.query.all()
	for case in cases:
		data.append({"id":case.id,"name":case.caseName,"desc":case.caseDesc})

	caseinfo = Template(caselist_template).render(
		cases = data
	)

	return caseinfo

@main.route("/newtestcase")
def newtestcase():
	return render_template("newtestcase.html")


@main.route("/writecase",methods=["POST"])
def writecase():
	global case_template
	name = request.form.get('casename')
	desc = request.form.get('casedesc')
	content = request.form.get('casecontent')
	libs,actions = [],[]

	for c in content.split("\r\n"):
		if c:
			libs.append(c) if c.startswith('from') or c.startswith("import") else actions.append(c)

	casecontent = Template(case_template.strip()).render(
		desc = desc,
		libs = libs,
		actions = actions
	)

	case = Testcase(
		name,
		desc,
		casecontent
	)
	db.session.add(case)
	db.session.commit()

	casefile = os.path.join(Config.CASE_FOLDER,"%s.py" %name)
	with open(casefile,'wb') as f:
		f.write(str(casecontent).encode('utf-8'))

	return "新增成功"

@main.route("/uploadcase",methods=["POST"])
def uploadcase():
	return "112"

@main.route("/testcases")
def testcases():
	testcases = Testcase.query.all()
	return render_template("testcases.html",testcases=testcases)

#=============================================================================================

@main.route("/elements",methods=["POST","GET"])
def elements():
	if request.method == "POST":
		data = "添加成功"
		try:
			ele = Appelement(
				request.form.get("findby"),
				request.form.get("name"),
				request.form.get("value")
			)
			db.session.add(ele)
			db.session.commit()
		except Exception as e:
			data = "添加失败:%s" %str(e)
		return data
	return render_template("elements.html")

@main.route("/elementdata")
def elementdata():
	elements = Appelement.query.all()
	data = [
		{
		"id": ele.id,
		"name":ele.name,
		"by":"<input id='findby_%s' type='text' class='form-control' value='%s'/>" %(ele.id,ele.findby),
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/>" %(ele.id,ele.value),
		"operate":"<button class='btn btn-default' onclick='saveeditelement(%s)'>保存</button> <button class='btn btn-danger' onclick='delelement(%s)'>删除</button>" %(ele.id,ele.id)
		} for ele in elements
	]
	return json.dumps(data)

@main.route("/saveeditelement/<int:id>")
def saveeditelement(id):
	try:
		ele = Appelement.query.filter_by(id=id).first()
		findby = request.args.get("findby")
		value = request.args.get("value")
		ele.findby = findby
		ele.value = value
		print(id,ele.findby,ele.value)
		db.session.add(ele)
		db.session.commit()
	except Exception as e:
		return "保存失败:%s" %str(e)
	return "保存成功"

@main.route("/delelement/<int:id>")
def delelement(id):
	try:
		ele = Appelement.query.filter_by(id=id).first()
		if ele:
			db.session.delete(ele)
			db.session.commit()
	except:
		return "删除失败"
	return "删除成功"