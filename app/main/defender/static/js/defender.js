function viewAppiumlog(casename) {
	$("#report_header").html('<span style="font-weight:bold">'+casename+'.appium_log</span>')
	var logcontent = ""
	datas[casename+"_appiumlog"].forEach(function(e) {
		logcontent += e
	})
	
	logviewer.getDoc().setValue(logcontent);
	
	setTimeout(function(){
		logviewer.refresh();
	},200);

}

function viewCaselog(casename) {
	$("#report_header").html('<span style="font-weight:bold">'+casename+'.case_log</span>');
	var logcontent = ""
	datas[casename+"_caselog"].forEach(function(e) {
		logcontent += e
	})
	
	logviewer.getDoc().setValue(logcontent)
	setTimeout(function(){
		logviewer.refresh();
	},200);
}

function viewScreenshots(casename) {
	$("#screenshot_body").html("")
	$("#screenshot_header").html('<span style="font-weight:bold">'+casename+'.screenshots</span>');
	var imgs = "";
	datas[casename+"_screenshots"].forEach(function (e) {
		imgs += '<li><div style="background-color:white;padding:2px"><div><h3>'+e[0]+'</h3></div><div><img src="'+e[1]+'" longdesc="#" width="384" height="683" alt="img" data-toggle="tooltip" data-placement="left" title="'+e[0]+'"/></div></div></li><hr>'
	})
	$("#screenshot_body").append(imgs)
}