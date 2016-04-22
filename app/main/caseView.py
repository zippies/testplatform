# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,flash,redirect,url_for
from ..models import db,Testcase

from . import main
import os,json

@main.route("/getcases")
def getcases():
	cases = Testcase.query.all()
	data = [{
		"id":"<input type='checkbox' name='choicedCase' id='case_{id}' value='{id}'/>".format(id=case.id),
		"name":case.caseName,
		"desc":case.caseDesc
	} for case in cases]

	return json.dumps(data)

@main.route("/writecase",methods=["POST"])
def writecase():
	info = {"result": True, "errorMsg": None}
	name = request.form.get('casename').strip()
	desc = request.form.get('casedesc').strip()
	content = request.form.get('casecontent')
	try:
		case = Testcase(
			name,
			desc,
			content
		)
		db.session.add(case)
		db.session.commit()
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}
	return jsonify(info)

@main.route("/editcase/<int:id>",methods=['POST'])
def editcase(id):
	info = {"result": True, "errorMsg": None}
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
		print("editcase failed:",e)
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

@main.route("/passcase/<int:id>")
def passcase(id):
	info = {"result":True,"errorMsg":None}
	try:
		testcase = Testcase.query.filter_by(id=id).first()
		if testcase and testcase.status == 0:
			testcase.status = 1
			db.session.add(testcase)
			db.session.commit()
		else:
			info = {"result":False,"errorMsg":"该用例不存在或已被删除"}
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}
	finally:
		return jsonify(info)

@main.route("/canclepasscase/<int:id>")
def canclepasscase(id):
	info = {"result":True,"errorMsg":None}
	try:
		testcase = Testcase.query.filter_by(id=id).first()
		if testcase and testcase.status == 1:
			testcase.status = 0
			db.session.add(testcase)
			db.session.commit()
		else:
			info = {"result":False,"errorMsg":"该用例不存在或已被删除"}
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}
	finally:
		return jsonify(info)
