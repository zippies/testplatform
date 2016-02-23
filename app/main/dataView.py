# -*- coding: utf-8 -*-
from flask import render_template,request
from ..models import db,Testdata,Conflictdata
from . import main
import json

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
		value = request.args.get("value")
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

#===================================================================

@main.route("/conflictdatas",methods=["POST","GET"])
def conflictdatas():
	if request.method == "POST":
		data = "添加成功"
		try:
			value = eval(request.form.get("value"))
			conflictdata = Conflictdata(
				request.form.get("name"),
				value
			)
			db.session.add(conflictdata)
			db.session.commit()
		except NameError:
			data = "添加失败:value 必须符合列表格式"
		except Exception as e:
			data = "添加失败:%s" %str(e)
		return data
	return render_template("conflictdatas.html")

@main.route("/conflictdata")
def conflictdata():
	conflictdatas = Conflictdata.query.all()
	data = [
		{
		"id": testdata.id,
		"name":testdata.name,
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/>" %(testdata.id,testdata.value),
		"operate":"<button class='btn btn-default' onclick='saveeditconflictdata(%s)'>保存</button> <button class='btn btn-danger' onclick='delconflictdata(%s)'>删除</button>" %(testdata.id,testdata.id)
		} for testdata in conflictdatas
	]
	return json.dumps(data)

@main.route("/saveeditconflictdata/<int:id>")
def saveeditconflictdata(id):
	try:
		conflictdata = Conflictdata.query.filter_by(id=id).first()
		value = request.args.get("value")
		conflictdata.value = value
		db.session.add(conflictdata)
		db.session.commit()
	except Exception as e:
		return "保存失败:%s" %str(e)
	return "保存成功"

@main.route("/delconflictdata/<int:id>")
def delconflictdata(id):
	try:
		conflictdata = Conflictdata.query.filter_by(id=id).first()
		if conflictdata:
			db.session.delete(conflictdata)
			db.session.commit()
	except:
		return "删除失败"
	return "删除成功"