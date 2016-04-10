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
	width = $(parent.document).width()/3
	layer.open({
		type: 2,
		title: 'API文档',
		shadeClose: true,
		shade: false,
		maxmin: true, //开启最大化最小化按钮
		offset: ['0px',width*2-5+"px"],
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

function viewdeviceinfo(){
    position_x = parent.document.body.clientWidth - 300;
    parent.layer.open({
        type:2,
        title:"当前连接的设备信息",
        shadeClose:true,
        shade:false,
        maxxin:false,
        offset:['100px',position_x+'px'],
        area:['300px','300px'],
        content:'/getconnecteddevice'
    })
}