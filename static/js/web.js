//mouseover mouseout
function mouse_over_out(){
	    //
    $(".edit a").mouseover(function(){
        $(this).css({"background":"#3D8DE2","cursor":"pointer"});
    });
    $(".edit a").mouseout(function(){
        $(this).css("background","#C8C6C6");
    });
    //

    //
    $(".delete").mouseover(function(){
        $(this).css({"background":"#FD739E","cursor":"pointer"});
    });
    $(".delete").mouseout(function(){
        $(this).css("background","#DDDDDD");
    });
    //   
     $("#entry_list a").mouseover(function(){
        $(this).css({"border-color":"#0CC65B","cursor":"pointer"});
    });
    $("#entry_list a").mouseout(function(){
        $(this).css("border-color","#CCCCCC");
    });
    //
}
//location:目标地点 obj 滚动的对象
function show_hide_scroll(location,obj){
	$(window).scroll(function(){
		if ($(this).scrollTop() > 100) {
			$(obj).show("slow");
		}else{
			$(obj).hide("slow");
		}
	});

	$(obj).click(function(){
		$.scrollTo($(location),800);
	});
}

//设置footer位置
function setFooter(){
    var footerHeight = 0;
    var footerTop = 0;
    footerHeight = $("#footer").height();
    footerTop =($(window).scrollTop()+$(window).height()-footerHeight)+"px";
    //console.log(footerHeight,footerTop,$(window).height(),$(window).scrollTop(),$(document.body).height());
    if ( $(window).height() > $(document.body).height() ) {
    	$("#footer-wrap").css({"position":"absolute"});
    }else {
    	$("#footer-wrap").css({"position":"static"});
    };
}

//archive delete按钮

//本地存储 对象标签和其日志标签
function localSave(obj,log_obj){
	var area = document.querySelector(obj);
	var value = obj+"_data"; //拼接字符串
	//判断是否从本地恢复数据
	if (!area.value) {
		area.value = window.localStorage.getItem(value);
	};
	//本地实时存储 记录值和时间戳
	area.addEventListener("keyup",function(){
		window.localStorage.setItem(value,area.value);
		window.localStorage.setItem("timestamp",(new Date()).getTime());
	}, false);

	//更新日志（可选）
	if (log_obj) {
		updatelog();
		setInterval(updatelog,10000); //10秒运行一次
		function updatelog(){
			var delta = 0;
			if (window.localStorage.getItem(value)) {
				delta = ((new Date()).getTime() - (new Date()).setTime(window.localStorage.getItem("timestamp")))/1000;
				document.querySelector(log_obj).innerHTML = "last saved:" + Math.round(delta) + "s ago.";
			}
		}
	}	
}

//获取url指定名字的参数
function getURLq(name){
    	var reg = new RegExp("^[?&]" + name + "=([^&]*)");
    	var r = window.location.search.substr(0).match(reg);
    	if (r != null) return unescape(r[1]);
    	return null;	
}

//ajax
//当前页 onPage 
//总页 sumPage  
//点击页 pageNum 
function queryPageNum(pageNum,send_data,sumPage,onPage){
	$.ajax({
		url:"/test",
		type:"GET",
		data:send_data,
		success:function(get_data){
			var data = eval("(" + get_data + ")");
				for (var i = 0; i < data.length; i++) {
				var id = data[i].id;
				var published = data[i].published;
				var html = data[i].html;
				var slug = data[i].slug;
				var title = data[i].title;
				var art = $("section").find(".article").eq(i);
				art.find("a").eq(0).attr("href","/entry/"+slug).text(title);
				art.find("a").eq(1).attr("href","/compose?id="+id);
				art.find(".text").eq(0).html(html);
				art.find(".date").eq(0).text(published);
				art = art.next();
			};
			//
			$("#entry_list a").remove();
			rebuildPageArea(pageNum,sumPage,onPage);
		}
	});
	return false;
}
function rebuildPageArea(pageNum,sumPage,onPage){
	var begin;
	var end = sumPage;
	if ( onPage <=2) {
		begin=1;
	}else {
		begin = pageNum -1;
		if (begin>sumPage-2) {
			begin = sumPage-2;
		};
	};
	AreaBuild(begin,end);
}

function AreaBuild(begin,end){
	var count =0;
	for (var i = begin; i <= end; i++) {
		//var pageArea = '<a href=/page?page_num='+i+'>'+i+'</a>';
		var pageArea = '<a class="rebulid_a" href="#">'+i+'</a>';
		//href=javascript:void(0) 不自动跳转到页首
		
		$("#entry_list").append(pageArea);
		count++;
		if (count>=3) break;
	};
}

//aside 
function asideGet(){
	$.ajax({
		url:"/aside",
		type:"get",
		data:null,
		success:function(msg){
			var data = eval("(" + msg + ")");
			for (var i = 0; i < data.length; i++) {
				var title = data[i].title;
				var slug = data[i].slug;
				var li_Area = '<li><a href=/entry/' + slug +'>'+title+'</a></li>';
				$(".rank #top_li").append(li_Area);
			};
		}
	})
}
