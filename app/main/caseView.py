# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,flash,redirect,url_for
from ..models import db,Testcase,Actionflow,Testjob
from .. import Config
from jinja2 import Template
from . import main
import os

caselist_template = '''
{% for case in cases %}
<tr>
	<td><input type="checkbox" name="choicedCase" id="case_{{ case.id }}" value={{ case.id }} /></td>
	<td id="casename_{{ case.id }}" class="casename">{{ case.name }}</td>
	<td id="casedesc_{{ case.id }}" class="casedesc">{{ case.desc }}</td>
</tr>
{% endfor %}
'''

@main.route("/getcases")
def getcases():
	data = []
	cases = Testcase.query.all()
	for case in cases:
		data.append({"id":case.id,"name":case.caseName,"desc":case.caseDesc})

	caseinfo = Template(caselist_template).render(
		cases = data
	)

	return caseinfo

@main.route("/writecase",methods=["POST"])
def writecase():
	name = request.form.get('casename').strip()
	desc = request.form.get('casedesc').strip()
	content = request.form.get('casecontent')
	case = Testcase(
		name,
		desc,
		content
	)
	db.session.add(case)
	db.session.commit()
	info = generateCase(case)
	return jsonify(info)

def generateCase(case):
	info = {"result":True,"errorMsg":None}
	job = Testjob.query.filter_by(status=1).first()
	if not job:
		try:
			with open(os.path.join(Config.CASE_FOLDER,"%s.py" %case.caseName),'wb') as f:
				libs,actions = [],[]
				for c in case.caseContent.split("\r\n"):
					if c:
						if c.strip().startswith('from') or c.strip().startswith("import"):
							libs.append(c)
						elif c.strip().startswith("{{") and c.strip().endswith("}}"):
							actionflow_name = c.strip("{}")
							actionflow = Actionflow.query.filter_by(name=actionflow_name).first()
							if actionflow:
								actions += actionflow.actions
						else:
							actions.append(c)

				content = Template(Config.case_template.strip()).render(
					desc = case.caseDesc,
					libs = libs,
					actions = actions
				)
				f.write(str(content).encode('utf-8'))
		except Exception as e:
			info["result"] = False
			info["errorMsg"] = str(e)

	return info

@main.route("/editcase/<int:id>",methods=['POST'])
def editcase(id):
	try:
		name = request.form.get('casename')
		desc = request.form.get('casedesc')
		content = request.form.get("casecontent")
		case = Testcase.query.filter_by(id=id).first()
		if case:
			case.caseName = name
			case.caseDesc = desc
			case.caseContent = content
			db.session.add(case)
			db.session.commit()
			info = generateCase(case)
			flash("编辑成功") if info["result"] else flash(info["errorMsg"])
		else:
			flash("该用例不存在")
	except Exception as e:
		print(e)
		flash("编辑失败:%s" %str(e))
	finally:
		return redirect(url_for(".testcases"))

@main.route("/delcase/<int:id>")
def delcase(id):
	info = {"result":True,"errorMsg":None}
	try:
		case = Testcase.query.filter_by(id=id).first()
		if case:
			db.session.delete(case)
			db.session.commit()
		else:
			info["result"] = False
			info["errorMsg"] = "用例不存在"
	except Exception as e:
		info["result"] = False
		info["errorMsg"] = str(e)
	finally:
		return jsonify(info)

@main.route("/uploadcase",methods=["POST"])
def uploadcase():
	return "该功能尚未支持"

@main.route("/testcases")
def testcases():
	testcases = Testcase.query.all()
	return render_template("testcases.html",testcases=testcases[::-1])



