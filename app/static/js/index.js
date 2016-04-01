window.onload = initNavBar;

function initNavBar() {
	document.documentElement.style.overflowX = 'hidden'
	$(".nav_item").click(function(){
		if(this.id == 'nav_alljob'){
			$("#content_detail").attr("src","/jobs")
		}else if(this.id == 'nav_newjob'){
			$("#content_detail").attr("src","/newjob")
		}else if(this.id == 'nav_alldevice'){
			$("#content_detail").attr("src","/devices")
		}else if(this.id == 'nav_allcase'){
			$("#content_detail").attr("src","/testcases")
		}else{
			alert("no such item:"+this.id)
		}
	})
}

function showapi(){
	width = $(parent.document).width()/4
	layer.open({
		type: 2,
		title: 'API文档',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ['0px',width*3-5+"px"],
		area: [width+"px","100%"],
		content: '/showapi'
	});
}

function viewreport(id){
	position_y = $(parent.document).height()/3

	layer.open({
		type: 2,
		title: 'TestReport',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ["0px", '0px'],
		area: ["100%","100%"],
		content: '/viewreport/'+id
	});
}