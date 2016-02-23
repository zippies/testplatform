# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,flash,redirect,url_for
from ..models import db,Testcase,Appelement,Testdata
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

@main.route("/newtestcase")
def newtestcase():
	return render_template("newtestcase.html")

@main.route("/writecase",methods=["POST"])
def writecase():
	name = request.form.get('casename')
	desc = request.form.get('casedesc')
	content = request.form.get('casecontent')
	case = Testcase(
		name,
		desc,
		content
	)
	db.session.add(case)
	db.session.commit()

	return "新增成功"

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
			flash("编辑成功")
		else:
			flash("该用例不存在")
	except Exception as e:
		flash("编辑失败:%s" %str(e))
	finally:
		return redirect(url_for(".testcases"))

@main.route("/delcase/<int:id>")
def delcase(id):
	resp = {"result":True,"info":None}
	try:
		case = Testcase.query.filter_by(id=id).first()
		if case:
			db.session.delete(case)
			db.session.commit()
		else:
			resp["result"] = False
			resp["info"] = "用例不存在"
	except Exception as e:
		resp["result"] = False
		resp["info"] = str(e)
	finally:
		return jsonify(resp)

@main.route("/uploadcase",methods=["POST"])
def uploadcase():
	return "112"

@main.route("/testcases")
def testcases():
	testcases = Testcase.query.all()
	return render_template("testcases.html",testcases=testcases[::-1])

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

#=============================================================================================

@main.route("/testdatas",methods=["POST","GET"])
def testdatas():
	if request.method == "POST":
		data = "添加成功"
		try:
			testdata = Testdata(
				request.form.get("name"),
				request.form.get("value")
			)
			db.session.add(testdata)
			db.session.commit()
		except Exception as e:
			data = "添加失败:%s" %str(e)
		return data
	return render_template("testdatas.html")

@main.route("/testdata")
def testdata():
	testdatas = Testdata.query.all()
	data = [
		{
		"id": testdata.id,
		"name":testdata.name,
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/>" %(testdata.id,testdata.value),
		"operate":"<button class='btn btn-default' onclick='saveedittestdata(%s)'>保存</button> <button class='btn btn-danger' onclick='deltestdata(%s)'>删除</button>" %(testdata.id,testdata.id)
		} for testdata in testdatas
	]
	return json.dumps(data)

@main.route("/saveedittestdata/<int:id>")
def saveedittestdata(id):
	try:
		testdata = Testdata.query.filter_by(id=id).first()
		name = request.args.get("name")
		value = request.args.get("value")
		testdata.name = name
		testdata.value = value
		db.session.add(testdata)
		db.session.commit()
	except Exception as e:
		return "保存失败:%s" %str(e)
	return "保存成功"

@main.route("/deltestdata/<int:id>")
def deltestdata(id):
	try:
		testdata = Testdata.query.filter_by(id=id).first()
		if testdata:
			db.session.delete(testdata)
			db.session.commit()
	except:
		return "删除失败"
	return "删除成功"