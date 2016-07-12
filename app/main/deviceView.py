# -*- coding: utf-8 -*-
from flask import render_template,redirect,url_for,request,jsonify,Response,flash
from ..models import Device,db
from . import main
from jinja2 import Template
import json,subprocess,re

@main.route("/newdevice",methods=["POST"])
def newdevice():
	info = {"result":True,"errorMsg":None}
	try:
		device = Device(
			request.form.get("phoneModel"),
			request.form.get("deviceName"),
			request.form.get("manufacturer"),
			request.form.get("platform"),
			request.form.get("platformVersion"),
			""
		)
		db.session.add(device)
		db.session.commit()
	except Exception as e:
		info = {"result":False,"errorMsg":str(e)}
	finally:
		flash(info)
		return redirect(url_for(".devices"))

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
	return render_template("devices.html",
							devices=devices
	)

device_template = '''
{% for device in devices %}
{% if device.status == 0%}
<label id="deviceitem" class="col-lg-3 col-md-4 col-sm-2">
	<input type="checkbox" onclick="showchange({{ device.id }})" name="choicedDevice" value="{{ device.id }}" {% if device.status != 0 %}disabled{% endif %}/>
	<div id="thumbnail_{{ device.id }}" style="border:1px solid #D9D9D9;border-radius:5px;padding:15px;">
		<div style="text-align:center;margin-bottom:15px">
			<img src="static/imgs/phone.png" alt="htc">
		</div>
		<table class="table table-bordered table-striped" id="deviceinfotable">
			<tbody>
				<tr>
					<th style="width:100px">phoneModel:</th>
					<td>
						<input class="deviceinfo_{{ device.id }}" name="phoneModel" type="text" value="{{ device.phoneModel }}" disabled="disabled" style="display:none">
						<span>{{ device.phoneModel }}</span>
					</td>
				</tr>
				<tr>
					<th>platform:</th>
					<td>
						<input class="deviceinfo_{{ device.id }}" name="platform" type="text" value="{{ device.platform }}" disabled="disabled" style="display:none">
						<span>{{ device.platform }}</span>
					</td>
				</tr>
				<tr>
					<th>paltformVersion:</th>
					<td>
						<input class="deviceinfo_{{ device.id }}" name="platformVersion" type="text" value="{{ device.platformVersion }}" disabled="disabled" style="display:none">
						<span>{{ device.platformVersion }}</span>
					</td>
				</tr>
				<tr>
					<th>deviceName:</th>
					<td>
						<input class="deviceinfo_{{ device.id }}" name="deviceName" type="text" value="{{ device.deviceName }}" disabled="disabled" style="display:none">
						<span>{{ device.deviceName }}</span>
					</td>
				</tr>
				<tr>
					<th>连接状态:</th>
					<td><font color="green">连接正常</font></td>
				</tr>
			</tbody>
		</table>
	</div>
</label>
{% endif %}
{% endfor %}
'''

def isadbok():
	cmd = "adb devices".split(" ")
	try:
		info = subprocess.run(cmd,stdout=subprocess.PIPE)
		if info.returncode == 0 and 'error' not in info.stdout.decode():
			return info.stdout.decode()
		else:
			restart = "adb kill-server".split(" ")
			info = subprocess.run(restart,stdout=subprocess.PIPE)
			if info.returncode == 0 and "successfully" in info.stdout.decode():
				return isadbok()
			else:
				return None
	except Exception as e:
		print(str(e))
		return None

def updatedevicesinfo():
	connected_devices = {}
	result = isadbok()
	if result:
		for info in result.split("\r\n"):
			if "List" in info:
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

adb_devices_template = """
<table style="width:100%">
	<thead>
		<tr style="width:100%">
			<td style="width:25%;text-align:center">设备序号</td>
			<td style="width:25%;text-align:center">连接状态</td>
			<td style="width:25%;text-align:center">系统版本</td>
			<td style="width:25%;text-align:center">手机型号</td>
		</tr>
	</thead>
	<tbody>
		{% for device in deviceinfos %}
			<tr style="text-align:center">
				<td>{{ device[0] }}</td>
				<td>{{ device[1] }}</td>
				<td>{{ device[2] }}</td>
				<td>{{ device[3] }}</td>
			</tr>
		{% endfor %}
	</tbody>
</table>
"""

@main.route("/getconnecteddevice")
def getconnecteddevice():
	resp = None
	info = isadbok()
	if info:
		deviceinfos = [inf.split("\t") for inf in info.split("\r\n")[1:] if inf.strip()]
		pattern_1 = re.compile(r"\[ro.product.brand\]: \[(.+)\]")
		pattern_2 = re.compile(r"\[ro.product.board\]: \[(.+)\]")
		for index,deviceinfo in enumerate(deviceinfos):
			cmd_1 = "adb -s %s shell getprop ro.build.version.release" %deviceinfo[0]
			info_1 = subprocess.run(cmd_1, stdout=subprocess.PIPE)
			if info_1.returncode == 0:
				deviceinfos[index].append(info_1.stdout.decode().strip())

			cmd_2 = "adb -s %s shell getprop" %deviceinfo[0]
			info_2 = subprocess.run(cmd_2, stdout=subprocess.PIPE)
			output = info_2.stdout.decode()
			if info_2.returncode == 0:
				productor = re.search(pattern_1,output).group(1)
				model = re.search(pattern_2,output).group(1)
				deviceinfos[index].append("%s %s" %(productor,model))

		if deviceinfos:
			print(1111,deviceinfos)
			resp = Template(adb_devices_template).render(
				deviceinfos=deviceinfos
			)
		else:
			resp = "<code>没有连接的设备</code>"
	else:
		resp = "<code>设备连接异常</code>"
	return resp

@main.route("/getdevicestatusfromjenkins")
def getdevicestatusfromjenkins():
	cmd = "adb devices".split(" ")
	devices = []
	result = subprocess.run(cmd,stdout=subprocess.PIPE)
	if result.returncode == 0:
		for info in result.stdout.decode().split("\r\n"):
			if "List" in info:
				continue
			elif 'device' in info:
				name = info.split('\t')[0].strip()
				device = Device.query.filter_by(deviceName=name).first()
				if device:
					devices.append(device.id)
			else:
				continue

	return json.dumps(devices)