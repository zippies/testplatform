function resizeFrame(){
	$(".thumbnail").width($("#deviceinfotable").width());
	ifm = parent.document.getElementById("content_detail");	
	var subWeb = parent.document.frames?parent.document.frames["content_detail"].document:ifm.contentDocument;
	if(ifm != null && subWeb != null) {
		ifm.height = subWeb.body.scrollHeight;
	}
}
