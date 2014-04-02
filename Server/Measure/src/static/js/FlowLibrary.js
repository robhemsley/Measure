/*
 *	Flow - Rob Hemsley (c) 2013
 *  -----------------------------------------------
 *
 *	Project Details go here
 *
 *	Version: 0.01 Alpha
 *	Date: 16/01/2013
 */
 
var $jq = null;
var TAG = "FlowLibrary::"

var running = false;

if (running == false) {
   	var running = true;	
   	setup();
}else{
	console.lon(TAG+"FlowLibrary Already Loaded!");		
}
	
function setup(){
   	console.log(TAG+"Library Called");
   	
	loadJQuery();
}
	
		
function loadJQuery(){
	loadScript('http://cdn.jquerytools.org/1.2.6/jquery.tools.min.js');
	//checkJQuery(0);
}
	
function loadScript(url){
	var p = document.createElement('script');
	p.type ='text/javascript';
	p.src = url;
	document.getElementsByTagName("head")[0].appendChild(p);
}
	
function checkJQuery(time_elapsed) {
    if (typeof jQuery == "undefined") {
  		if (time_elapsed <= 5000) {
   	    	setTimeout("checkJQuery(" + (time_elapsed + 200) + ")", 200);
		} else {
			console.log(TAG+"jQuery Load TimedOut")
        }
    } else {
    	console.log(TAG+"JQuery Loaded");
    }
}

		


	

	

	

	