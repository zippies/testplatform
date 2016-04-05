from flask import Flask,render_template,request,jsonify,redirect,url_for,flash
from ..models import db,Actionflow
from . import main

@main.route("/actionflows")
def actionflows():
	actionflows = Actionflow.query.all()
	return render_template("actionflows.html",actionflows=actionflows)

@main.route("/newactionflow",methods=["Post"])
def newactionflow():
	info = {"result":True,"errorMsg":None}
	name = request.form.get("name")
	actions = [action.strip() for action in request.form.get("actions").split("\r\n") if action.strip()]

	try:
		actionflow = Actionflow(name,actions)
		db.session.add(actionflow)
		db.session.commit()
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}

	return jsonify(info)

@main.route("/delflow/<int:id>")
def delflow(id):
	info = {"result":True,"errorMsg":None}
	try:
		actionflow = Actionflow.query.filter_by(id=id).first()
		if actionflow:
			db.session.delete(actionflow)
			db.session.commit()
		else:
			info = {"result":False,"errorMsg":"该动作流不存在或已被删除"}
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}
	finally:
		return jsonify(info)

@main.route("/editflow/<int:id>",methods=["POST"])
def editflow(id):
	try:
		name = request.form.get('name')
		actions = [action.strip() for action in request.form.get("actions").split("\r\n") if action.strip()]
		print(name,actions)
		actionflow = Actionflow.query.filter_by(id=id).first()

		if actionflow:
			actionflow.name = name
			actionflow.actions = actions

			db.session.add(actionflow)
			db.session.commit()
			flash("编辑成功")
		else:
			flash("该动作流不存在")
	except Exception as e:
		flash("编辑失败:%s" %str(e))
	finally:
		return redirect(url_for(".actionflows"))