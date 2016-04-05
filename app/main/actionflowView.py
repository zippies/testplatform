from flask import Flask,render_template,request,jsonify
from ..models import db,Actionflow
from . import main

@main.route("/actionflows")
def actionflows():
	return render_template("actionflows.html")

@main.route("/newactionflow",methods=["Post"])
def newactionflow():
	info = {"result":True,"errorMsg":None}
	name = request.form.get("name")

	actions,keys = [],[]
	for k,v in request.form.items():
		if k == "name" or not v.strip():
			continue
		else:
			keys.append(int(k))

	keys.sort()

	for key in keys:
		actions.append(request.form.get(str(key)))

	try:
		actionflow = Actionflow(name,actions)
		db.session.add(actionflow)
		db.session.commit()
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}

	return jsonify(info)