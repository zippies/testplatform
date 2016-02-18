# -*- coding: utf-8 -*-
from flask import render_template,redirect,url_for,request,jsonify
from . import main
from ..models import Device,db
from flask.ext.login import login_required


@main.route("/newdevice",methods=["GET","POST"])
def newdevice():
	if request.method == "POST":
		device = Device(
			request.form.get("phoneModel"),
			request.form.get("deviceName"),
			request.form.get("manufacturer"),
			request.form.get("platform"),
			request.form.get("platformVersion"),
			request.form.get("resolution")
		)
		db.session.add(device)
		db.session.commit()
		return redirect(url_for('.devices'))
	else:
		return render_template("newdevice.html")

@main.route("/editdevice")
def editdevice():
	resp = {"result":True,"info":None}
	try:
		device = Device.query.filter_by(id=int(request.args.get('id'))).first()
		device.phoneModel = request.args.get("phoneModel")
		device.deviceName = request.args.get("deviceName")
		device.manufacturer = request.args.get("manufacturer")
		device.platform = request.args.get("platform")
		device.platformVersion = request.args.get("platformVersion")
		device.resolution = request.args.get("resolution")
		device.status = request.args.get("status")
		db.session.add(device)
		db.session.commit()
	except Exception as e:
		resp["result"] = False
		resp["info"] = str(e)
	return jsonify(resp)

@main.route("/deldevice/<int:id>")
def deldevice(id):
	resp = {"result":True,"info":None}
	try:
		device = Device.query.filter_by(id=id).first()
		db.session.delete(device)
		db.session.commit()
	except Exception as e:
		resp["result"] = False
		resp["info"] = str(e)
	return jsonify(resp)

@main.route("/devices")
def devices():
	devices = Device.query.all()
	deviceinfos = {
		"platform":["android","ios"],
		"platformversion":["4.4.4","4.4.3","4.4.2","4.3","4.2"],
		"resolution":["1920*800","1280*768"],
		"	":["HUAWEI","APPLE","XIAOMI"],
		"status":["可用","不可用"]
	}
	return render_template("devices.html",
							deviceinfos=deviceinfos,
							devices=devices
	)



device_template = '''
{% for device in devices %}
<label id="deviceitem" class="col-sm-6 col-md-3">
	<input type="checkbox" name="choicedDevice" value="{{ device.id }}" />
	<div class="thumbnail">
		<img src="static/imgs/phone.png" alt="htc">
		<table class="table table-bordered table-striped">
			<tbody>
				<tr>
					<th>phoneModel:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="phoneModel" type="text" value="{{ device.phoneModel }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>platform:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="platform" type="text" value="{{ device.platform }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>paltformVersion:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="platformVersion" type="text" value="{{ device.platformVersion }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>resolution:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="resolution" type="text" value="{{ device.resolution }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>status:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="status" type="text" value="{{ device.status }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>deviceName:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="deviceName" type="text" value="{{ device.deviceName }}" disabled="disabled"></td>
				</tr>
			</tbody>
		</table>
	</div>
</label>
{% endfor %}
'''

@main.route("/getdevices")
def getdevices():
	from jinja2 import Template
	global device_template
	devices = Device.query.all()
	deviceinfo = Template(device_template).render(
		devices=devices
	)
	return deviceinfo