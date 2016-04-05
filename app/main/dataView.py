# -*- coding: utf-8 -*-
from flask import render_template,request,flash,redirect,url_for
from ..models import db,Testdata,Conflictdata
from . import main
import json

@main.route("/testdatas",methods=["POST","GET"])
def testdatas():
	if request.method == "POST":
		data = "添加成功"
		try:
			testdata = Testdata.query.filter_by(name=request.form.get("name")).first()
			if testdata:
				data = "名称已被占用"
			else:
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
		"id": i+1,
		"name":"<input id='name_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(testdata.id,testdata.name,testdata.name),
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(testdata.id,testdata.value,testdata.value),
		"operate":"<button class='btn btn-default' onclick='saveedittestdata(%s)'>保存</button> <button class='btn btn-danger' onclick='deltestdata(%s)'>删除</button>" %(testdata.id,testdata.id)
		} for i,testdata in enumerate(testdatas)
	]
	return json.dumps(data)

@main.route("/saveedittestdata/<int:id>")
def saveedittestdata(id):
	try:
		testdata = Testdata.query.filter_by(id=id).first()
		name = request.args.get("name")
		value = request.args.get("value")
		print(name,value)
		testdata.value = value
		testdata.name = name
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

@main.route("/import/testdata",methods=["POST"])
def importtestdata():
	count = 0
	file = request.files.get("testdatafile")
	testdatasdata = json.loads(file.read().decode("utf-8"))["data"]
	for e in testdatasdata:
		elem = Testdata.query.filter_by(name=e["TestdataName"]).first()
		if elem:
			print("exists:",e["TestdataName"])
		else:
			testdata = Testdata(
				e["TestdataName"],
				e["TestdataValue"]
			)
			db.session.add(testdata)
			db.session.commit()
			count += 1
	flash("导入完成！共导入%s条通用测试数据" %count)
	return redirect(url_for(".testdatas"))

#===================================================================

@main.route("/conflictdatas",methods=["POST","GET"])
def conflictdatas():
	if request.method == "POST":
		data = "添加成功"
		try:
			conflictdata = Conflictdata.query.filter_by(name=request.form.get("name")).first()
			if conflictdata:
				data = "名称已被占用"
			else:
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
		"id": i+1,
		"name":"<input id='name_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(testdata.id,testdata.name,testdata.name),
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(testdata.id,json.dumps(testdata.value),json.dumps(testdata.value)),
		"operate":"<button class='btn btn-default' onclick='saveeditconflictdata(%s)'>保存</button> <button class='btn btn-danger' onclick='delconflictdata(%s)'>删除</button>" %(testdata.id,testdata.id)
		} for i,testdata in enumerate(conflictdatas)
	]
	return json.dumps(data)

@main.route("/saveeditconflictdata/<int:id>")
def saveeditconflictdata(id):
	try:
		conflictdata = Conflictdata.query.filter_by(id=id).first()
		name = request.args.get("name")
		value = eval(request.args.get("value"))
		conflictdata.name = name
		conflictdata.value = value
		db.session.add(conflictdata)
		db.session.commit()
		print(conflictdata.value)
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

@main.route("/import/conflictdata",methods=["POST"])
def importconflictdata():
	count = 0
	file = request.files.get("conflictdatafile")
	conflictdatasdata = json.loads(file.read().decode("utf-8"))["data"]
	for e in conflictdatasdata:
		elem = Conflictdata.query.filter_by(name=e["TestdataName"]).first()
		if elem:
			print("exists:",e["TestdataName"])
		else:
			conflictdata = Conflictdata(
				e["TestdataName"],
				eval(e["TestdataValue"])
			)
			db.session.add(conflictdata)
			db.session.commit()
			count += 1
	flash("导入完成！共导入%s条冲突测试数据" %count)
	return redirect(url_for(".conflictdatas"))