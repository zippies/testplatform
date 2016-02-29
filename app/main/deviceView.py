# -*- coding: utf-8 -*-
from flask import render_template,redirect,url_for,request,jsonify,Response,flash
from flask.ext.login import login_required
from subprocess import Popen,PIPE
from ..models import Device,db
from . import main
import json


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
		flash("添加成功")
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
	<input type="checkbox" onclick="showchange({{ device.id }})" name="choicedDevice" value="{{ device.id }}" {% if device.status != 0 %}disabled{% endif %}/>
	<div class="thumbnail" id="thumbnail_{{ device.id }}">
		<img src="static/imgs/phone.png" alt="htc">
		<table class="table table-bordered table-striped" id="deviceinfotable">
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
					<th>deviceName:</th>
					<td><input class="deviceinfo_{{ device.id }}" name="deviceName" type="text" value="{{ device.deviceName }}" disabled="disabled"></td>
				</tr>
				<tr>
					<th>连接状态:</th>
					<td>{% if device.status == 0%}<font color="green">连接正常</font>{%else%}<font color="red">连接异常</font>{% endif %}</td>
				</tr>
			</tbody>
		</table>
	</div>
</label>
{% endfor %}
'''

def updatedevicesinfo():
	cmd = "adb devices"
	connected_devices = {}
	p = Popen(cmd,stdout=PIPE,shell=True)
	for info in p.stdout.readlines():
		info = info.decode()
		if 'List' in info:
			continue
		elif 'offline' in info:
			name,state = [n.strip() for n in info.split('\t') if n.strip()]
			connected_devices[name] = -1
		elif 'unauthorized' in info:
			name,state = [n.strip() for n in info.split('\t') if n.strip()]
			connected_devices[name] = -2
		elif 'device' in info:
			name,state = [n.strip() for n in info.split('\t') if n.strip()]
			connected_devices[name] = 0
		else:
			continue
	
	p.kill()

	devices = Device.query.all()
	for device in devices:
		if device.deviceName not in connected_devices.keys():
			device.status = -3
		else:
			device.status = connected_devices[device.deviceName]

		db.session.add(device)
		db.session.commit()

@main.route("/getdevices")
def getdevices():
	from jinja2 import Template
	global device_template
	updatedevicesinfo()
	devices = Device.query.all()
	deviceinfo = Template(device_template).render(
		devices=devices
	)
	return deviceinfo

@main.route("/getDeviceStatus")
def getdevicestatus():
	updatedevicesinfo()

	devices = Device.query.all()
	status = {}
	for device in devices:
		status[str(device.id)] = str(device.status)
	status = json.dumps(status)

	return Response("data:"+status+"\n\n",mimetype="text/event-stream")