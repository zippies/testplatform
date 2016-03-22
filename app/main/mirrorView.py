# -*- coding: utf-8 -*-
from flask import render_template,request,jsonify,redirect,url_for
from werkzeug.utils import secure_filename
from threading import Thread
from xml.dom import minidom
from datetime import datetime
from subprocess import Popen,PIPE
from .. import Config
from .mirror.basecase import AndroidDevice
from . import main
import os,re,platform,requests,copy

_id = 0
apk = None
appium_port = 14111
bootstrap_port = 14112
appium_log_level = "error"
driver = None
nodeDatas = []
nodeinfos = {}
frameinfos = {}
reversedframe = False
reverseframe = {}
deviceStatus = {}
packageName = ""
main_activity = ""
current_activity = ""

def getChildNodes(node):
	nodes = [n for n in node.childNodes if n.nodeName !='#text']
	return len(nodes)

def parseBounds(bound_str):
	global driver,_id,reversedframe
	start_p,end_p = bound_str.strip("[]").split("][")
	start_x,start_y = start_p.split(",")
	end_x,end_y = end_p.split(",")

	if int(end_x) > driver.device_width or int(end_y) > driver.device_height:
		reversedframe = True
	else:
		reversedframe = False

	height = round((int(end_y) - int(start_y))*0.4)
	width = round((int(end_x) -int(start_x))*0.4)
	return (round(int(start_x)*0.4),round(int(start_y)*0.4),height,width)

def setXpath(node,xpaths):
	xpathinfo = None
	if node.nodeName != "hierarchy":
		index = int(node.getAttribute("index"))
		parent_node = node.parentNode
		if index > 0:
			deep = 1
			for n in parent_node.childNodes:
				if n.nodeName == node.nodeName and int(n.getAttribute("index")) < int(node.getAttribute("index")):
					deep += 1
			xpathinfo = "%s[%s]" %(node.nodeName,deep)
		else:
			xpathinfo = node.nodeName

		xpaths.append(xpathinfo)

		setXpath(parent_node,xpaths)

		return xpaths

def setNodeInfo(node,nodeinfos,frameinfos):
	global _id
	nodeinfo = {}
	notes = {}
	xpaths = []
	cared_attributes = ["index",
						"text",
						"class",
						"package",
						"content-desc",
						"checkable",
						"checked",
						"clickable",
						"enabled",
						"focusable",
						"focused",
						"scrollable",
						"long-clickable",
						"password",
						"selected",
						"bounds",
						"resource-id",
						"instance"
						]
	for attr in cared_attributes:
		nodeinfo[attr] = node.getAttribute(attr)

	if node.hasAttribute("bounds"):
		bounds = parseBounds(node.getAttribute("bounds"))
		notes["x1"],notes["y1"],notes["height"],notes["width"] = bounds
		notes["note"] = node.nodeName
		notes["id"] = _id

	xpaths = setXpath(node,xpaths)

	if xpaths:
		nodeinfo["xpath"] = "//%s" %"/".join(xpaths[::-1])
	else:
		nodeinfo["xpath"] = ""

	nodeinfo['id'] = _id
	nodeinfos[_id] = nodeinfo
	frameinfos[_id] = notes

def getNodes(index,node,nodeinfos,frameinfos):
	global _id
	if node.nodeName != "#text":
		datadict = None
		childNodeCount = getChildNodes(node)
		_id += 1
		setNodeInfo(node,nodeinfos,frameinfos)
		
		if childNodeCount > 0:
			datadict = {
				"id": _id,
				"text": "(%s)%s" %(index,node.nodeName),
				"href":"#",
				"tags":['%s' %childNodeCount],
				"nodes":[]
			}
		else:
			datadict = {
				"id": _id,
				"text": "(%s)%s" %(index,node.nodeName),
				"href":"#",
				"tags":['%s' %childNodeCount]
			}

		for i,n in enumerate([n for n in node.childNodes if n.nodeName !="#text"]):
			data = getNodes(i+1,n,nodeinfos,frameinfos)
			if data:
				datadict['nodes'].append(data)

		return datadict


def getDeviceState():
	global deviceStatus
	cmd = "adb devices"
	devices = []
	p = Popen(cmd,stdout=PIPE,shell=True)
	for info in p.stdout.readlines():
		info = info.decode()
		if 'List' in info:
			continue
		elif 'offline' in info or 'unauthorized' in info or 'device' in info:
			device = {}
			name,state = [n.strip() for n in info.split('\t') if n.strip()]
			device["deviceName"] = name
			device["state"] = state
			if ":" in name:
				device["replacedName"] = name.replace(".","").replace(":","")
			else:
				device["replacedName"] = name
			devices.append(device)
			if name not in deviceStatus.keys():
				deviceStatus[name] = False
		else:
			continue
	
	p.kill()
	
	return devices

def is_Appium_Alive(port):
	'''
		检查指定端口的appium是否已启动
	'''
	try:
		if requests.get('http://localhost:%s/wd/hub' %port,timeout=(0.5,0.5)).status_code == 404:
			return True
		else:
			return False
	except Exception as e:
		return False

def stopAppium():
	'''
		关闭所有appium服务
	'''
	driver = None
	if platform.system() == 'Windows':
		info = os.popen("netstat -ano|findstr %s" %appium_port).readline()
		if "LISTENING" in info:
			pid = info.split("LISTENING")[1].strip()
			print("Stop pid:",pid)
			os.system("ntsd -c q -p %s" %pid)
	else:
		os.system("killall node")


@main.route("/mirror/connect/<devicename>",methods=['POST'])
def connectDevice(devicename):
	global deviceStatus
	appiumlog = os.path.join(os.getcwd(),"logs",datetime.now().strftime("%Y_%m_%d_%H_%M_%S"),"appium.log")
	os.makedirs(os.path.dirname(appiumlog))
	cmd = "appium\
			 -a localhost \
			 -p %s \
			 -bp %s \
			 -g %s \
			 --log-timestamp \
			 --log-level %s \
			 -U %s \
			 --log-no-colors" %(appium_port,bootstrap_port,appiumlog,appium_log_level,devicename)
	p = Thread(target=os.system,args=(cmd,))
	if is_Appium_Alive(appium_port):
		for device in deviceStatus.keys():
			deviceStatus[device] = False
		stopAppium()

	p.setDaemon(True)
	p.start()
	info = "Starting Appium on port : %s bootstrap_port: %s for device %s" %(appium_port,bootstrap_port,devicename)
	deviceStatus[devicename] = True
	return info

@main.route("/mirror/disconnect")
def disconnect():
	global driver,deviceStatus
	resp = {"status":True,"info":"disconnect success!"}
	try:
		driver.quit()
		stopAppium()
		for key in deviceStatus.keys():
			deviceStatus[key] = False
	except:
		resp["status"] = False
		resp["info"] = "appium已断开连接,请重新连接"

	return jsonify(resp)

@main.route("/mirror/isappiumready")
def isAppiumReady():
	data = None
	if is_Appium_Alive(appium_port):
		data = {"status":True,"info":"appium is ready!"}
	else:
		data = {"status":False,"info":"appium is not ready,keep waitting.."}

	return jsonify(data)

@main.route("/mirror/swipe/<direction>")
def swipe(direction):
	global driver,frameinfos
	resp = {"status":True,"info":None}
	id = request.args.get("id")
	px = request.args.get("px")
	elem = frameinfos.get(int(id))
	start_x,start_y = round((elem['x1']+round(elem['width']/2))/0.4),round((elem['y1']+round(elem['height']/2))/0.4)
	if direction == 'up':
		end_x,end_y = start_x,start_y - int(px)
	elif direction == 'down':
		end_x,end_y = start_x,start_y + int(px)
	elif direction == 'left':
		end_x,end_y = start_x - int(px),start_y
	elif direction == 'right':
		end_x,end_y = start_x + int(px),start_y
	else:
		resp = {"status":False,"info":"No such direction:%s" %direction}

	if 0 < end_x < driver.device_width and 0 < end_y < driver.device_height:
		try:
			driver.swipe((start_x,start_y),(end_x,end_y))
			freshScreen()
		except:
			resp["status"] = False
			resp["info"] = "长时间无操作,appium已断开连接,请重新启动"
	else:
		resp = {"status":False,"info":"swipe out of device screen"}
	return jsonify(resp)

@main.route("/mirror/click/<id>")
def click(id):
	global driver,frameinfos
	resp = {"status":True,"info":None}
	elem = frameinfos.get(int(id))
	try:
		x,y = round((elem['x1']+round(elem['width']/2))/0.4),round((elem['y1']+round(elem['height']/2))/0.4)
		driver.click_point(x,y)
		freshScreen()
	except:
		resp["status"] = False
		resp["info"] = "长时间无操作,appium已断开连接,请重新启动"
	
	return jsonify(resp)

@main.route("/mirror/sendtext/<id>")
def sendText(id):
	global driver,nodeinfos
	resp = {"status":True,"info":None}
	text = request.args.get('text')
	elem = nodeinfos[int(id)]
	elem_id = elem.get("resource-id")
	try:
		if elem_id:
			driver.input('id',elem_id,text)
			freshScreen()
		else:
			resp["status"] = False
			resp["info"] = "Make sure this element has an id"
	except:
		resp["status"] = False
		resp["info"] = "长时间无操作,appium已断开连接,请重新启动"

	return jsonify(resp)

@main.route("/mirror/cleartext/<id>")
def clearText(id):
	global driver,nodeinfos
	resp = {"status":True,"info":None}
	elem = nodeinfos[int(id)]
	elem_id = elem.get("resource-id")
	try:
		if elem_id:
			driver.click('id',elem_id)
			for i in range(len(elem.get("text"))):
				driver.press_keycode(67)
			freshScreen()
		else:
			resp["status"] = False
			resp["info"] = "Make sure this element has an id"
	except:
		resp["status"] = False
		resp["info"] = "长时间无操作,appium已断开连接,请重新启动"

	return jsonify(resp)

@main.route("/mirror/sendkeycode/<code>")
def back(code):
	global driver
	resp = {"status":True,"info":None}
	try:
		driver.press_keycode(code)
		freshScreen()
	except:
		resp["status"] = False
		resp["info"] = "长时间无操作,appium已断开连接,请重新启动"

	return jsonify(resp)

@main.route("/mirror/fresh")
def fresh():
	resp = {"status":True,"info":None}
	try:
		freshScreen(0)
	except Exception as e:
		print(1111111111111,e)
		resp["status"] = False
		resp["info"] = "长时间无操作,appium已断开连接,请重新启动"

	return jsonify(resp)


@main.route("/mirror/getapp",methods=["POST"])
def getAppInfo():
	global packageName,main_activity,apk
	f = request.files['file']
	fname = secure_filename(f.filename)
	apk = os.path.join(Config.UPLOAD_FOLDER,fname)
	f.save(apk)
	cmd_activity = "aapt d badging %s|findstr launchable-activity" %apk
	cmd_package = "aapt d badging %s|findstr package" %apk
	activity = Popen(cmd_activity,stdout=PIPE,shell=True)
	package = Popen(cmd_package,stdout=PIPE,shell=True)
	main_activity = activity.stdout.read().decode().split("name='")[1].split("'")[0]
	packageName = package.stdout.read().decode().split("name='")[1].split("'")[0]
	activity.kill()
	package.kill()

	return redirect(url_for(".mirror"))


def freshScreen(seconds=2):
	global _id,driver,nodeDatas,nodeinfos,frameinfos,current_activity
	_id = 0
	nodeDatas,nodeinfos,frameinfos = [],{},{}
	current = os.path.join(Config.UPLOAD_FOLDER,"current.png")
	print(current)
	driver.save_screen(current,seconds=seconds)
	current_activity = driver.current_activity
	page_source = driver.page_source
	page_source = re.sub("[\x00-\x08\x0b-\x0c\x0e-\x1f]+",u"",page_source)
	try:
		root = minidom.parseString(page_source).documentElement
	except Exception as e:
		print(e)

	for i,node in enumerate([n for n in root.childNodes if n.nodeName !="#text"]):
		if node.nodeName != "#text":
			datadict = getNodes(i+1,root,nodeinfos,frameinfos)
			nodeDatas.append(datadict)

@main.route("/mirror/showcloser")
def showCloser():
	global frameinfos,reverseframe,reversedframe
	x,y = request.args.get('x'),request.args.get('y')
	closer = 0
	minner = 100000000
	frame = frameinfos if not reversedframe else reverseframe
	for i,v in frame.items():
		if i and v and v['x1']<int(x)<v['x1']+v['width'] and v['y1']<int(y)<v['y1']+v['height']:
			if v['width']*v['height'] < minner:
				minner =  v['width'] * v['height'] 
				closer = i

	return str(closer)

@main.route("/mirror/getdata")
def getdata():
	global nodeDatas,nodeinfos,frameinfos,current_activity
	resp = {
		"nodeDatas":nodeDatas,
		"nodeinfos":nodeinfos,
		"frameinfos":frameinfos,
		"current_activity":current_activity
	}

	return jsonify(resp)

@main.route("/mirror/isconnect")
def isconnect():
	global deviceStatus
	resp = {"status":True,"info":None}
	for value in deviceStatus.values():
		if value:
			break
	else:
		resp["status"] = False
		resp["info"] = "No device connected!"

	return jsonify(resp)

@main.route('/mirror/getscreen',methods=["GET","POST"])
def getScreen():
	global driver,nodeDatas,nodeinfos,frameinfos,reversedframe,reverseframe,packageName,main_activity,apk
	if reversedframe:
		reverseframe = copy.deepcopy(frameinfos)
		for id in reverseframe.keys():
			if id - 1:
				x1 = round(driver.device_width*0.4-reverseframe[id]['y1']-reverseframe[id]['height'])
				y1 = reverseframe[id]['x1']
				width = reverseframe[id]['height']
				height = reverseframe[id]['width']
				reverseframe[id]['x1'],reverseframe[id]['y1'],reverseframe[id]['width'],reverseframe[id]['height'] = x1,y1,width,height

	if request.method == "POST":
		devicename = request.args.get("devicename")
		capabilities = {
				"app":apk,
				"appPackage":packageName,
				"appActivity":main_activity,
				"newCommandTimeout":86400,
				"noSign":True,
				#"unicodeKeyboard":True,
				#"resetKeyboard":True,
				"deviceName":devicename,
				"platformName":"Android",
				"platformVersion":"4.4"
		}

		driver = AndroidDevice("http://localhost:%s/wd/hub" %appium_port,capabilities)
		freshScreen()
		return "ok"



	return render_template(
							"deviceinfo.html",
							nodeDatas=nodeDatas,
							nodeinfos=nodeinfos,
							frameinfos=frameinfos if not reversedframe else reverseframe
						)

@main.route('/mirror')
def mirror():
	global nodeDatas,deviceStatus,packageName,main_activity
	
	devices = getDeviceState()

	return render_template(
							"mirror.html",
							devices=devices,
							packageName=packageName,
							main_activity=main_activity,
							deviceStatus=deviceStatus
	)