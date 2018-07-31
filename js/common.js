function isPC(){
   var userAgentInfo = navigator.userAgent;
   var Agents = new Array("Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod");
   var flag = true;
   for (var v = 0; v < Agents.length; v++) {
       if (userAgentInfo.indexOf(Agents[v]) > 0) { flag = false; break; }
   }
   return flag;
}

/**
 * [isMobile 判断平台]
 * @param test: 0:iPhone    1:Android
 */
function isMobile(){
    var u = navigator.userAgent, app = navigator.appVersion;
    if(/AppleWebKit.*Mobile/i.test(navigator.userAgent) || (/MIDP|SymbianOS|NOKIA|SAMSUNG|LG|NEC|TCL|Alcatel|BIRD|DBTEL|Dopod|PHILIPS|HAIER|LENOVO|MOT-|Nokia|SonyEricsson|SIE-|Amoi|ZTE/.test(navigator.userAgent))){
     if(window.location.href.indexOf("?mobile")<0){
      try{
       if(/iPhone|mac|iPod|iPad/i.test(navigator.userAgent)){
        return '0';
       }else{
        return '1';
       }
      }catch(e){}
     }
    }else if( u.indexOf('iPad') > -1){
        return '0';
    }else{
        return '1';
    }
};
function openPopup(){
	$('.x-popup-fixed').removeClass('hide');
}
function closePopup(){
	$('.x-popup-fixed').addClass('hide');
}
function closeNav(){
	$('.mobile-nav').addClass('hide-nav');
	$('.x-container').removeClass('all-move-right').addClass('all-move-left');
	$('.black-mask').addClass('hide');
}
function openNav(){
	$('.mobile-nav').removeClass('hide-nav');
	$('.x-container').addClass('all-move-right').removeClass('all-move-left');
	$('.black-mask').removeClass('hide');
}
function showDrop(ele){
	$(ele).siblings('.mobile-nav-ul').toggleClass('hide')
}
function openWhat(){
	$('.x-popup-fixed2').removeClass('hide');
}
function closePopup2(){
	$('.x-popup-fixed2').addClass('hide');
}

function closeSoon(){
	$('.soon-fixed').addClass('hide')
}
function openSoon(){
	if(isPC()){
		$('.soon-fixed').removeClass('hide')
	}else{
		$('.mobile-soon').removeClass('hide');
		var timer = setTimeout(function(){
			$('.mobile-soon').addClass('hide')
			clearTimeout(timer);
		},1000)
	}
}