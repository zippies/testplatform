window.onload = initNavBar;

function initNavBar() {
	document.documentElement.style.overflowX = 'hidden'
	$(".nav_item").click(function(){
		if(this.id == 'nav_job'){
			$("#content_detail").attr("src","/jobs")
		}else if(this.id == 'nav_newdevice'){
			$("#content_detail").attr("src","/newdevice")
		}else if(this.id == 'nav_alldevice'){
			$("#content_detail").attr("src","/devices")
		}else if(this.id == 'nav_testcase'){
			$("#content_detail").attr("src","/testcases")
		}else if(this.id == 'nav_newjob'){
			$("#content_detail").attr("src","/newjob")
		}else if(this.id == 'nav_alljob'){
			$("#content_detail").attr("src","/jobs")
		}else if(this.id == 'nav_newcase'){
			$("#content_detail").attr("src","/newtestcase")
		}else if(this.id == 'nav_allcase'){
			$("#content_detail").attr("src","/testcases")
		}else if(this.id == 'nav_normaldata'){
			$("#content_detail").attr("src","/testdatas")
		}else if(this.id == 'nav_conflictdata'){
			$("#content_detail").attr("src","/conflictdatas")
		}else{
			alert("no such item:"+this.id)
		}
	})
}

function showapi(){
	layer.open({
		type: 2,
		title: 'API文档',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ['350px','10px'],
		content: '/showapi'
	});
}

function openmirror(){
	layer.open({
		type: 2,
		title: 'Mirror',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ['570px', '10px'],
		content: '/mirror'
	});
}

function viewreport(id){
	layer.open({
		type: 2,
		title: 'TestReport',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ['50px', '500px'],
		area: ['1200px','800px'],
		content: '/viewreport/'+id
	});
}