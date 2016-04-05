# -*- coding: utf-8 -*-
from flask import render_template,request,redirect,url_for,flash,jsonify
from ..models import db,Appelement
from . import main
import json

@main.route("/elements",methods=["POST","GET"])
def elements():
	if request.method == "POST":
		data = "添加成功"
		try:
			ele = Appelement.query.filter_by(name=request.form.get("name")).first()
			if ele:
				data = "名称已被占用"
			else:
				ele = Appelement.query.filter_by(value=request.form.get("value")).first()
				if ele and ele.value == request.form.get("value"):
					data = "该值的元素已存在,名称为:%s" %ele.name
				else:
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
		"id": i+1,
		"name":"<input id='name_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(ele.id,ele.name,ele.name),
		"by":"<input id='findby_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(ele.id,ele.findby,ele.findby),
		"value":"<input id='value_%s' type='text' class='form-control' value='%s'/><label style='display:none'>%s</label>" %(ele.id,ele.value,ele.value),
		"operate":"<button class='btn btn-default' onclick='saveeditelement(%s)'>保存</button> <button class='btn btn-danger' onclick='delelement(%s)'>删除</button>" %(ele.id,ele.id)
		} for i,ele in enumerate(elements)
	]
	return json.dumps(data)

@main.route("/saveeditelement/<int:id>")
def saveeditelement(id):
	try:
		ele = Appelement.query.filter_by(id=id).first()
		name = request.args.get("name")
		findby = request.args.get("findby")
		value = request.args.get("value")
		ele.name = name
		ele.findby = findby
		ele.value = value
		print(id,ele.name,ele.findby,ele.value)
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

@main.route("/import/elements",methods=["POST"])
def importelements():
	count = 0
	file = request.files.get("elementfile")
	elementsdata = json.loads(file.read().decode("utf-8"))["data"]
	for e in elementsdata:
		elem = Appelement.query.filter_by(name=e["ElementName"]).first()
		if elem:
			print("exists:",e["ElementName"])
		else:
			elem = Appelement.query.filter_by(value=e["ElementValue"]).first()
			if elem and elem.value == e["ElementValue"]:
				continue
			else:
				ele = Appelement(
					e["FindBy"],
					e["ElementName"],
					e["ElementValue"]
				)
				db.session.add(ele)
				db.session.commit()
				count += 1
	flash("导入完成！共导入%s条元素信息" %count)
	return redirect(url_for(".elements"))

@main.route("/showelementname")
def showelementname():
	info = {"exist":False,"name":None}
	resourceid = request.args.get("resourceid")
	text = request.args.get("text")
	xpath = request.args.get("xpath")

	if resourceid:
		ele = Appelement.query.filter(db.and_(Appelement.findby == "id",Appelement.value == resourceid)).first()
		if ele:
			info = {"exist":True,"name":ele.name}
		else:
			ele = Appelement.query.filter(db.and_(Appelement.findby == "xpath",Appelement.value == xpath)).first()
			if ele:
				info = {"exist":True,"name":ele.name}
			else:
				if text:
					ele = Appelement.query.filter(db.and_(Appelement.findby == "name",Appelement.value == text)).first()
					if ele:
						info = {"exist":True,"name":ele.name}

	return jsonify(info)

	