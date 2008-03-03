var rcache = new Object();

var extractor = new Object();

extractor.dlCollection = null;

extractor.dlBuffer = null;

extractor.dlCurrentFile = null;

extractor.bCompleted = false;

extractor.http = null;

extractor.currentURL = function(){
    // get current url
    return getBrowser().currentURI.spec;
};

extractor.onProgress = function(e){
    //
    try{
	var progress = document.getElementById('media-dl-progress');
	var percentComplete = (e.position / e.totalSize)*100;
	progress.value = percentComplete;
    } catch(e) {
	alert(e);
    }
};
    
extractor.onError = function(e){
    //
    alert(e);
};

extractor.download = function(url){

    try{
	http = new XMLHttpRequest();
	var dl_desc = document.getElementById('media-dl-desc');
	dl_desc.setAttribute("value","Downloading: " + url );
	function readystatechange(e){
	    if(http.status == 200){
		if(http.readyState == 4){
		    //alert("Done");
		    var lstbx = document.getElementById('media-lst');
		    lstbx.disabled = false;
		    var progress = document.getElementById('media-dl-progress');
		    progress.value = 0;
		    var btn = document.getElementById('cache-button');
		    btn.disabled = false;
		    var dllst = document.getElementById('downloaded-items');
		    dllst.appendItem(url);
		    var dl_desc = document.getElementById('media-dl-desc');
		    dl_desc.setAttribute("value","Download Finished" );
		    this.bCompleted = true;
		    return http.responseText;
		}  
		if(http.readyState == 1){
		    this.bCompleted = false;
		    //alert("loading...");
		}
		if(http.readyState == 0){
		    this.bCompleted = false;
		    //alert("unititialized");
		}
	    } 
	    
	}

	http.onreadystatechange = readystatechange; 
	http.onprogress = this.onProgress;
	http.open("GET", url, true);
	//http.onload = onLoad;
	http.onerror = this.onError;
	http.send(null);
	// alert("File Size in Bytes: " + content_length);
	//     alert("File Type: " + content_type);
	var msg = "Downloading...";
	dl_desc.setAttribute("value",msg);
    } catch(e){
	alert(e);
	var lstbx = document.getElementById('media-lst');
	lstbx.disabled = false;
    }
    
};


extractor.window = function(){    
    try{
	var mainWindow = window.content;
	return mainWindow;
    } catch(e){
	alert(e);
    }
}
    
extractor.imgs_subset =  function(regex){
    try{
	var frag = this.fragmentElement();
	var links=frag.getElementsByTagName("IMG");
    } catch(e){
	alert(e);
    }
    try{
	var img_arr = new Array();      
	for (var i = 0; i < links.length; i++){
	    if (regex.test(links[i].src)){
		if (img_arr.indexOf(links[i]) == -1){
		    img_arr.push(links[i]);
		}
	    }
	}
	return img_arr;
    } catch(e){
	alert(e);
    }
}


extractor.link_subset = function(regex){
    try{
	var frag = this.fragmentElement();
	var links=frag.getElementsByTagName("A");
    } catch(e){
	alert(e);
    }
    try{
	var link_arr = new Array();      
	for (var i = 0; i < links.length; i++){
	    if (regex.test(links[i].href)){
		if (link_arr.indexOf(links[i]) == -1){
		    link_arr.push(links[i]);
		}
	    }
	}
	return link_arr;
    } catch(e){
	alert(e);
    }
}
    
extractor.all_links = function(){
    try{
	var frag = this.fragmentElement();
	var links=frag.getElementsByTagName("A");
    } catch(e){
	alert(e);
    }
    try{
	var link_arr = new Array();      
	for (var i = 0; i < links.length; i++){
	    if (link_arr.indexOf(links[i]) == -1){
		link_arr.push(links[i]);
	    }
	}
	return link_arr;
    } catch(e){
	alert(e);
    }
}

    
extractor.selectedText =null;

extractor.selectedTextFragment =null;

extractor.run = function(){
    try{
	var txt = this.selection();
	this.selectedText = txt;
	if (txt == ''){
	    alert("Please select a portion of this page");
	} else {
	    var pdf_regex = /.pdf$/i;
	    var doc_regex = /.doc$/i;
	    var pdfs = this.link_subset(pdf_regex);
	    var docs = this.link_subset(doc_regex);

	    var img_regex = /.jpg$|.png$/i;
	    //fixme: create settings so you can in fact get gif images!
	    var imgs = this.imgs_subset(img_regex);
	    var links = this.all_links();
	    var matched_links = {'pdfs':pdfs,
				 'docs':docs,
				 'imgs':imgs,
				 'links':links};
	    return matched_links;
	}
    } catch(e){
	var a = new Array();
	return {'pdfs':a,'docs':a,'imgs':a,'links':a};
    }
}

extractor.htmlTitle = null;

extractor.fragmentElement = function(){
    try{
	var txt = this.selection();
	var rng = txt.getRangeAt(0);
	var frag = rng.cloneContents();
	var element = content.document.createElement("DIV");    
	element.id = "rcache-tmp-div-img";
	element.appendChild(frag);
	return element;
	
    } catch(e){
	alert(e);
    }
}

extractor.reportXUL = function(){
    try{
	//alert("after try");
	var win = this.window();
	var txt = win.getSelection();
	this.htmlTitle = win.document.title;
	var title = win.document.title;
	var matched_links = this.run();
	//alert(matched_links['pdfs']);
	//fiinish collcting page pieces here:
	//var title = this.thetitle();
	if (this.selectedText != ''){
	    var report_win = this.extractor_win();
	    //alert(report_win);
	    var loadFunction = function() {
		var pdflst = report_win.document.getElementById('media-lst');
		for (var i = 0; i < matched_links['pdfs'].length; i++){
		    pdflst.appendItem(matched_links['pdfs'][i].href);	
		}
		
		for (var i = 0; i < matched_links['imgs'].length; i++){
		    pdflst.appendItem(matched_links['imgs'][i].src);	
		}
		for (var i = 0; i < matched_links['docs'].length; i++){
		    pdflst.appendItem(matched_links['docs'][i].href);	
		}
		
		var link_lst = report_win.document.getElementById('linkbox');
		//alert(matched_links['links']);
		for (var i = 0; i < matched_links['links'].length; i++){
		    link_lst.appendItem(matched_links['links'][i].href);
		}
		
		report_win.document.title = "rcache collector 0.2 | " +  title;
		var selTex =
		report_win.document.getElementById('selectedtext');
		//alert(this.selectedText);
		selTex.setAttribute("value",txt);
		var pgTitle =
		report_win.document.getElementById('pagetitle');
		pgTitle.setAttribute("value",win.document.title);
		var pgUrl =
		report_win.document.getElementById('url');
		pgUrl.setAttribute("value",win.document.location);
		
		function openlink(){
		    try{
			//open link in new browser window!
			url = this.getSelectedItem(0);
			if (url.label != ''){
			    var win = window.open(url.label,"external_link"); 
			}
		    } catch(e) {
			alert(e);
		    }
		}
		link_lst.addEventListener("dblclick", openlink, false);
		
	    };
	    
	    report_win.addEventListener("load", loadFunction, false);
	} else {
	    //pass
	}
    } catch(e){
	alert(e);
    }
    
}

extractor.extractor_win = function(){
    var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(Components.interfaces.nsIWindowWatcher);
    var win = ww.openWindow(null,
			    "chrome://rcache/content/rcache_collector.xul", 
    			    "status", 
    			    "chrome,resizable", null);
    return win;
}

extractor.startDownload = function(){
    //alert("starting");
    if (this.dlCollection == null){
	this.dlCollection = new Array();
    }
    var lstbx = document.getElementById('media-lst');
    url = lstbx.getSelectedItem(0);
    //alert(url.label);
    var progress = document.getElementById('media-dl-progress');
    progress.value = 0;
    //lstbx.disabled = true;
    try{
	var dlData = this.download(url.label);
	var dlObj = {'data':dlData,'url':url.label};
	this.dlCollection.push(dlObj);
	var dlObj = null;
    } catch(e){
	alert(e);
    }
    
}

extractor.startUpload = function(){
    var btn = document.getElementById('rcache-upload-doc');
    btn.disabled = true;
    //create new xmlhttprequest
    //get current file
    //do POST
}

extractor.showFileDetails = function(){
    alert("implement a remove item function");
}

extractor.selection = function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var selected_txt=wndw.getSelection();
    return selected_txt;
}

extractor.post_after_confirm = function(){
    var bCompleted = false;
    setInterval(this.evalComplete, 100);
    this.http_collector();
}
 
//postUrl: 'https://collect.rcache.com/postcache/',

extractor.postUrl: 'http://127.0.0.1:8000/postcache/';

extractor.loginUrl: "https://collect.rcache.com/loginxul/";


extractor.http_collector = function(){
    if (document.getElementById('selectedtext').value !=""){
	var serverurl = this.postUrl;
	var http = new XMLHttpRequest();
	var winurl = document.getElementById('url').value;
	var link = 'entry_url=' + encodeURIComponent(winurl) + '&';
	var wintitle = document.getElementById('pagetitle').value;
	var name = 'entry_name=' + encodeURIComponent(wintitle) + '&';
	var windesc = document.getElementById('pagetitle').value;
	var desc = 'description=' + encodeURIComponent(windesc) + '&';
	var wintext = document.getElementById('selectedtext').value;
	var text = 'text_content=' + encodeURIComponent(wintext) + '&';
	var wintags = document.getElementById('tags').value;
	var tags = 'tags=' + encodeURIComponent(wintags) + '&';
	//deal with listbox that holds the links and imgs...
	var links_qs = 'links_qs' + "=";
	try {
	    var lnkBx = document.getElementById('linkbox');
	    lnkBx.selectAll();
	    if (lnkBx.selectedCount > 0){
		var links = new Array();
		for (var i=0;i < lnkBx.selectedCount; i++){
		    var item = lnkBx.selectedItems[i].label;
		    links.push(item);
		}
		var links_qs = links_qs + links.join("||sep||");
	    } 	  
	} catch(e) {
	    //alert(e);
	}
      
	var imgs_qs = 'imgs_qs' + "=";
	try {
	    var imgBx = document.getElementById('imgbox');
	    imgBx.selectAll();
	    if (imgBx.selectedCount > 0){
		var imgs = new Array();
		for (var i=0;i < imgBx.selectedCount; i++){
		    var item = imgBx.selectedItems[i].label;
		    imgs.push(item);
		}
		imgs_qs = imgs_qs + imgs.join("||sep||");
		//alert(imgs_qs);
	    }	  
	} catch(e) {
	    //alert(e);
	}
      
	links_qs = links_qs + '&';
	//alert(links_qs);
	//make query string for POST request
	var params = link + name + desc + text + tags + links_qs + imgs_qs;
      
	http.onreadystatechange = function() {
	    //Call a function when the state changes.
	    if(http.status == 200) {
		if(http.readyState == 4){
		    // weird response handling
		    if(eval(http.responseText)=='done'){
			document.getElementById('progress').hidden = true;
			bCompleted = true;
		    }
		    else if(eval(http.responseText) == 'login_error'){
			document.getElementById('cache-button').disabled = false;
			document.getElementById('progress').hidden = true;
			window.open(this.loginUrl,
				    "rcache-loginxul",
				    "menubar=no,location=no,resizable=no,scrollbars=yes,status=yes,width=348,height=195");
			bCompleted = false;
		    } else {
			//no idea what is what??
			document.getElementById('cache-button').disabled = false;
			alert(http.responseText);
		    }
		}
	    } else {
		bCompleted = false;
		document.getElementById('cache-button').disabled = false;
		alert(http.responseText);
	    }
	}
	document.getElementById('progress').hidden = false;
	document.getElementById('cache-button').disabled = true;
	http.open("POST", serverurl, true);
	//Send the proper header infomation along with the request
	http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
	http.setRequestHeader("Content-length", params.length);
	http.setRequestHeader("Connection", "close");
	http.send(params);
    } else {
	alert("No Text is Selected");
	return false;
    }
}

extractor.evalComplete = function(){
    if (bCompleted == true) {
	bCompleted = false;
	window.setInterval(rcache.statusMsg, 100);
	window.setInterval(window.close, 1200);
    }
}

extractor.statusMsg: function(){
    window.document.getElementById('statusmsg').value = "Sucessful rCache.";
}

extractor.confirm = function(){
    var links = new Array();
    var imgs = new Array();
    //get a hrefs
    try{
	var txt = this.selection();
	var rng = txt.getRangeAt(0);
	var frag = rng.cloneContents();
	var element = content.document.createElement("DIV");    
	element.id = "rcache-tmp-div";
	element.appendChild(frag);
	var linkObjs = element.getElementsByTagName("A");
	for (var i = 0; i < linkObjs.length; i++){
	    if(linkObjs[i].href !=''){
		links.push(linkObjs[i].href);
	    }
	}
    } catch(e){
	//alert(e);
	//silently pass
    }
    //get img src strings
    try{
	var txt = this.selection();
	var rng = txt.getRangeAt(0);
	var frag = rng.cloneContents();
	var element = content.document.createElement("DIV");    
	element.id = "rcache-tmp-div-img";
	element.appendChild(frag);
	var imgObjs = element.getElementsByTagName("IMG");
	for (var i = 0; i < imgObjs.length; i++){
	    if (imgObjs[i].src !=''){
		imgs.push(imgObjs[i].src);
	    }
	}
    } catch(e){
	//alert(e);
	//silently pass
    }
    
    if (txt !=""){
	var title = this.thetitle();
	var confirmwin = this.collector_win();
	var loadFunction = function() {
	    var selTex =
	    confirmwin.document.getElementById('selectedtext');
	    selTex.setAttribute("value",txt);
	    var pgTitle =
	    confirmwin.document.getElementById('pagetitle');
	    pgTitle.setAttribute("value",this.thetitle());
	    var pgUrl =
	    confirmwin.document.getElementById('url');
	    pgUrl.setAttribute("value",this.currentURL());
	    
	    var linksLst = confirmwin.document.getElementById('linkbox');
	    
	    for (var i = 0; i < links.length; i++){
		linksLst.appendItem(links[i]);	
	    }
	    var imgLst = confirmwin.document.getElementById('imgbox');
	    for (var i = 0; i < imgs.length; i++){
		imgLst.appendItem(imgs[i]);	
	    }
	};
	confirmwin.addEventListener("load", loadFunction, false); 
    } else {
	//paste the clipboard into txt
	alert("rCache: Please highlight a portion of this page.");
    }
}
 
extractor.thetitle = function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var title=wndw.document.title;
    return title;
}

extractor.collector_win = function(){
    var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"]
    .getService(Components.interfaces.nsIWindowWatcher);
    var win = ww.openWindow(null,
			    "chrome://rcache/content/rcache_collector.xul", 
    			    "status", 
    			    "chrome,resizable", null);
    return win;
}
   












// var extractor = {

//  dlCollection: null,

//  dlBuffer: null,
 
//  dlCurrentFile: null,

//  currentURL: function(){
//     return getBrowser().currentURI.spec;
//   },

//  bCompleted: false,

//  http: null,

//  onProgress: function(e){
//     try{
//       var progress = document.getElementById('pdf-dl-progress');
//       //progress.style = "";
//       var percentComplete = (e.position / e.totalSize)*100;
//       //alert("trying to set progress");
//       progress.value = percentComplete;
//     } catch(e) {
//       alert(e);
//     }
//   },
 
//  onError: function(e){
//     alert(e);
//   },

//  download: function(url){
//     try{
//     http = new XMLHttpRequest();
//     var dl_desc = document.getElementById('pdf-dl-desc');
//     dl_desc.setAttribute("value","Downloading: " + url );


//     function readystatechange(e){
//       if(http.status == 200){
// 	if(http.readyState == 4){
// 	  //alert("Done");
// 	  var lstbx = document.getElementById('pdf-lst');
// 	  lstbx.disabled = false;
// 	  var progress = document.getElementById('pdf-dl-progress');
// 	  progress.value = 0;
// 	  var btn = document.getElementById('cache-button');
// 	  btn.disabled = false;
// 	  var dllst = document.getElementById('downloaded-items');
// 	  dllst.appendItem(url);
// 	  var dl_desc = document.getElementById('pdf-dl-desc');
// 	  dl_desc.setAttribute("value","Download Finished" );
// 	  this.bCompleted = true;
// 	  return http.responseText;
// 	}  
// 	if(http.readyState == 1){
// 	  this.bCompleted = false;
// 	  //alert("loading...");
// 	}
// 	if(http.readyState == 0){
// 	  this.bCompleted = false;
// 	  //alert("unititialized");
// 	}
//       } 
      
//     }

//     http.onreadystatechange = readystatechange; 
//     http.onprogress = this.onProgress;
//     http.open("GET", url, true);
//     //http.onload = onLoad;
//     http.onerror = this.onError;
//     http.send(null);
//     // alert("File Size in Bytes: " + content_length);
// //     alert("File Type: " + content_type);
//     var msg = "Downloading...";
//     dl_desc.setAttribute("value",msg);
//     } catch(e){
//     alert(e);
//     var lstbx = document.getElementById('pdf-lst');
//     lstbx.disabled = false;
//   }
//   },
 
//  window: function(){
//     try{
//       var mainWindow = window.content;
//       return mainWindow;
//     } catch(e){
//       alert(e);
//     }
//   },
 
//  imgs_subset: function(regex){
//     try{
//       //var win = this.window();
//       var frag = this.fragmentElement();
//       var links=frag.getElementsByTagName("IMG");
//     } catch(e){
//       alert(e);
//     }
//     try{
//       var img_arr = new Array();      
//       for (var i = 0; i < links.length; i++){
// 	if (regex.test(links[i].src)){
// 	  if (img_arr.indexOf(links[i]) == -1){
// 	    img_arr.push(links[i]);
// 	  }
// 	}
//       }
//       return img_arr;
//     } catch(e){
//       alert(e);
//     }
//   },
 
//  link_subset: function(regex){
//     try{
//       //var win = this.window();
//       var frag = this.fragmentElement();
//       //alert(frag);
//       var links=frag.getElementsByTagName("A");
//     } catch(e){
//       alert(e);
//     }
//     try{
//       var link_arr = new Array();      
//       for (var i = 0; i < links.length; i++){
// 	if (regex.test(links[i].href)){
// 	  if (link_arr.indexOf(links[i]) == -1){
// 	    link_arr.push(links[i]);
// 	  }
// 	}
//       }
//       //alert(link_arr);
//       return link_arr;
//     } catch(e){
//       alert(e);
//     }
//   },
 
//  all_links: function(){
//     try{
//       //var win = this.window();
//       var frag = this.fragmentElement();
//       //alert(frag);
//       var links=frag.getElementsByTagName("A");
//     } catch(e){
//       alert(e);
//     }
//     try{
//       var link_arr = new Array();      
//       for (var i = 0; i < links.length; i++){
// 	if (link_arr.indexOf(links[i]) == -1){
// 	  link_arr.push(links[i]);
// 	}
//       }
//       //alert(link_arr);
//       return link_arr;
//     } catch(e){
//       alert(e);
//     }
//   },

//  selectedText : null,

//  selectedTextFragment : null,

//  run: function(){
//     try{
//       var txt = this.selection();
//       this.selectedText = txt;

//       if (txt == ''){
// 	alert("Please select a portion of this page");
//       } else {
// 	var pdf_regex = /.pdf$/i;
// 	var doc_regex = /.doc$/i;
// 	var pdfs = this.link_subset(pdf_regex);
// 	var docs = this.link_subset(doc_regex);
// 	//var imgs_arr = this.imgs();
// 	var img_regex = /.jpg$|.png$/i;
// 	//fixme: create settings so you can in fact get gif images!
// 	var imgs = this.imgs_subset(img_regex);
// 	var links = this.all_links();
// 	//alert(pdfs);
// 	var matched_links = {'pdfs':pdfs,
// 			     'docs':docs,
// 			     'imgs':imgs,
// 			     'links':links};
	
// 	//alert(matched_links);
// 	return matched_links;
//       }
//     } catch(e){
//       var a = new Array();
//       return {'pdfs':a,'docs':a,'imgs':a,'links':a};
//     }
//   },
 
//  htmlTitle: null,

//  fragmentElement: function(){
//     try{
     
// 	var txt = this.selection();
// 	var rng = txt.getRangeAt(0);
// 	var frag = rng.cloneContents();
// 	var element = content.document.createElement("DIV");    
// 	element.id = "rcache-tmp-div-img";
// 	element.appendChild(frag);
// 	return element;
    
//     } catch(e){
//       alert(e);
//     }
//   },

//  reportXUL: function(){
    
//     try{
//       //alert("after try");
//       var win = this.window();
//       var txt = win.getSelection();
//       this.htmlTitle = win.document.title;
//       var title = win.document.title;
//       var matched_links = this.run();
//       //alert(matched_links['pdfs']);
//       //fiinish collcting page pieces here:
//       //var title = this.thetitle();
      


//       if (this.selectedText != ''){
// 	var report_win = this.extractor_win();
// 	//alert(report_win);
// 	var loadFunction = function() {
// 	  var pdflst = report_win.document.getElementById('pdf-lst');
// 	  for (var i = 0; i < matched_links['pdfs'].length; i++){
// 	    pdflst.appendItem(matched_links['pdfs'][i].href);	
// 	  }
	
// 	  for (var i = 0; i < matched_links['imgs'].length; i++){
// 	    pdflst.appendItem(matched_links['imgs'][i].src);	
// 	  }
// 	  for (var i = 0; i < matched_links['docs'].length; i++){
// 	    pdflst.appendItem(matched_links['docs'][i].href);	
// 	  }
	
// 	  var link_lst = report_win.document.getElementById('linkbox');
// 	  //alert(matched_links['links']);
// 	  for (var i = 0; i < matched_links['links'].length; i++){
// 	    link_lst.appendItem(matched_links['links'][i].href);
// 	  }
	
// 	  report_win.document.title = "rcache collector 0.2 | " +  title;
// 	  var selTex =
// 	  report_win.document.getElementById('selectedtext');
// 	  //alert(this.selectedText);
// 	  selTex.setAttribute("value",txt);
// 	  var pgTitle =
// 	  report_win.document.getElementById('pagetitle');
// 	  pgTitle.setAttribute("value",win.document.title);
// 	  var pgUrl =
// 	  report_win.document.getElementById('url');
// 	  pgUrl.setAttribute("value",win.document.location);

// 	  function openlink(){
// 	    try{
// 	      //open link in new browser window!
// 	      url = this.getSelectedItem(0);
// 	      if (url.label != ''){
// 		var win = window.open(url.label,"external_link"); 
// 	      }
// 	    } catch(e) {
// 	      alert(e);
// 	    }
// 	  }
// 	  link_lst.addEventListener("dblclick", openlink, false);
	  
// 	};
	
// 	report_win.addEventListener("load", loadFunction, false);
//       } else {
// 	//pass
//       }
//     } catch(e){
//       alert(e);
//     }

//   },

//  extractor_win: function(){
//     var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(Components.interfaces.nsIWindowWatcher);
//     var win = ww.openWindow(null,
// 			    "chrome://rcache/content/rcache_collector.xul", 
//     			    "status", 
//     			    "chrome,resizable", null);
//     return win;
//   },

//  startDownload: function(){
//     //alert("starting");
//     if (this.dlCollection == null){
//       this.dlCollection = new Array();
//     }
//     var lstbx = document.getElementById('pdf-lst');
//     url = lstbx.getSelectedItem(0);
//     //alert(url.label);
//     var progress = document.getElementById('pdf-dl-progress');
//     progress.value = 0;
//     //lstbx.disabled = true;
//     try{
//       var dlData = this.download(url.label);
//       var dlObj = {'data':dlData,'url':url.label};
//       this.dlCollection.push(dlObj);
//       var dlObj = null;
//     } catch(e){
//       alert(e);
//     }
    
//   },

//  startUpload: function(){
//     var btn = document.getElementById('rcache-upload-doc');
//     btn.disabled = true;
//     //create new xmlhttprequest
//     //get current file
//     //do POST
//   },

//  showFileDetails: function(){
//     alert("implement a remove item function");
//   },

//  selection: function(){
//     var wndw=document.commandDispatcher.focusedWindow;
//     var selected_txt=wndw.getSelection();
//     return selected_txt;
//   },

//  post_after_confirm: function(){
//     var bCompleted = false;
//     setInterval(this.evalComplete, 100);
//     this.http_collector();
//   },
 
 
//  //postUrl: 'https://collect.rcache.com/postcache/',
//  postUrl: 'http://127.0.0.1:8000/postcache/',

//  loginUrl: "https://collect.rcache.com/loginxul/",

//  http_collector: function(){
//     if (document.getElementById('selectedtext').value !=""){
//       var serverurl = this.postUrl;
//       var http = new XMLHttpRequest();

//       var winurl = document.getElementById('url').value;
//       var link = 'entry_url=' + encodeURIComponent(winurl) + '&';
      
//       var wintitle = document.getElementById('pagetitle').value;
//       var name = 'entry_name=' + encodeURIComponent(wintitle) + '&';

//       var windesc = document.getElementById('pagetitle').value;
//       var desc = 'description=' + encodeURIComponent(windesc) + '&';

//       var wintext = document.getElementById('selectedtext').value;
//       var text = 'text_content=' + encodeURIComponent(wintext) + '&';

//       var wintags = document.getElementById('tags').value;
//       var tags = 'tags=' + encodeURIComponent(wintags) + '&';

//       //deal with listbox that holds the links and imgs...
//       var links_qs = 'links_qs' + "=";
//       try {
// 	var lnkBx = document.getElementById('linkbox');
// 	lnkBx.selectAll();
// 	if (lnkBx.selectedCount > 0){
// 	    var links = new Array();
// 	    for (var i=0;i < lnkBx.selectedCount; i++){
// 	      var item = lnkBx.selectedItems[i].label;
// 	      links.push(item);
// 	    }
// 	    var links_qs = links_qs + links.join("||sep||");
// 	} 	  
//       } catch(e) {
// 	//alert(e);
//       }
      
//       var imgs_qs = 'imgs_qs' + "=";
//       try {
// 	var imgBx = document.getElementById('imgbox');
// 	imgBx.selectAll();
// 	if (imgBx.selectedCount > 0){
// 	  var imgs = new Array();
// 	  for (var i=0;i < imgBx.selectedCount; i++){
// 	    var item = imgBx.selectedItems[i].label;
// 	    imgs.push(item);
// 	  }
// 	  imgs_qs = imgs_qs + imgs.join("||sep||");
// 	  //alert(imgs_qs);
// 	}	  
//       } catch(e) {
// 	//alert(e);
//       }
      
//       links_qs = links_qs + '&';
//       //alert(links_qs);
      
//       //make query string for POST request
//       var params = link + name + desc + text + tags + links_qs + imgs_qs;
      
//       http.onreadystatechange = function() {
// 	//Call a function when the state changes.
// 	if(http.status == 200) {
// 	  if(http.readyState == 4){
// 	    // weird response handling
// 	    if(eval(http.responseText)=='done'){
// 	      document.getElementById('progress').hidden = true;
// 	      bCompleted = true;
// 	    }
// 	    else if(eval(http.responseText) == 'login_error'){
// 	      document.getElementById('cache-button').disabled = false;
// 	      document.getElementById('progress').hidden = true;
// 	      window.open(this.loginUrl,
// 			  "rcache-loginxul",
// 			  "menubar=no,location=no,resizable=no,scrollbars=yes,status=yes,width=348,height=195");
// 	      bCompleted = false;
// 	    } else {
// 	      //no idea what is what??
// 	      document.getElementById('cache-button').disabled = false;
// 	      alert(http.responseText);
// 	    }
// 	  }
// 	} else {
// 	  bCompleted = false;
// 	  document.getElementById('cache-button').disabled = false;
// 	  alert(http.responseText);
// 	}
//       }
//       document.getElementById('progress').hidden = false;
//       document.getElementById('cache-button').disabled = true;
//       http.open("POST", serverurl, true);
//       //Send the proper header infomation along with the request
//       http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
//       http.setRequestHeader("Content-length", params.length);
//       http.setRequestHeader("Connection", "close");
//       http.send(params);
//     } else {
//       alert("No Text is Selected");
//       return false;
//     }
//   },

//  evalComplete: function(){
//     if (bCompleted == true) {
//       bCompleted = false;
//       window.setInterval(rcache.statusMsg, 100);
//       window.setInterval(window.close, 1200);
//     }
//   },

//  statusMsg: function(){
//     window.document.getElementById('statusmsg').value = "Sucessful rCache.";
//   },

//  confirm: function(){
//     var links = new Array();
//     var imgs = new Array();
//     //get a hrefs
//     try{
//       var txt = this.selection();
//       var rng = txt.getRangeAt(0);
//       var frag = rng.cloneContents();
//       var element = content.document.createElement("DIV");    
//       element.id = "rcache-tmp-div";
//       element.appendChild(frag);
//       var linkObjs = element.getElementsByTagName("A");
//       for (var i = 0; i < linkObjs.length; i++){
// 	links.push(linkObjs[i].href);
//       }
//     } catch(e){
//       //alert(e);
//       //silently pass
//     }
//     //get img src strings
//     try{
//       var txt = this.selection();
//       var rng = txt.getRangeAt(0);
//       var frag = rng.cloneContents();
//       var element = content.document.createElement("DIV");    
//       element.id = "rcache-tmp-div-img";
//       element.appendChild(frag);
//       var imgObjs = element.getElementsByTagName("IMG");
//       for (var i = 0; i < imgObjs.length; i++){
// 	imgs.push(imgObjs[i].src);
//       }
//     } catch(e){
//       //alert(e);
//       //silently pass
//     }

//     if (txt !=""){
//       var title = this.thetitle();
//       var confirmwin = this.collector_win();
//       //var progress = confirmwin.document.getElementById('progress');
//       //progress.hidden = false;
//       var loadFunction = function() {
// 	var selTex =
// 	confirmwin.document.getElementById('selectedtext');
// 	selTex.setAttribute("value",txt);
// 	var pgTitle =
// 	confirmwin.document.getElementById('pagetitle');
// 	pgTitle.setAttribute("value",this.thetitle());
// 	var pgUrl =
// 	confirmwin.document.getElementById('url');
// 	pgUrl.setAttribute("value",this.currentURL());

// 	var linksLst = confirmwin.document.getElementById('linkbox');

// 	for (var i = 0; i < links.length; i++){
// 	  linksLst.appendItem(links[i]);	
// 	}
// 	var imgLst = confirmwin.document.getElementById('imgbox');
// 	for (var i = 0; i < imgs.length; i++){
// 	  imgLst.appendItem(imgs[i]);	
// 	}
//       };
//       confirmwin.addEventListener("load", loadFunction, false); 
//     } else {
//       //paste the clipboard into txt
//       alert("rCache: Please highlight a portion of this page.");
//     }
//   },

//  thetitle: function(){
//     var wndw=document.commandDispatcher.focusedWindow;
//     var title=wndw.document.title;
//     return title;
//   },

//  collector_win: function(){
//     var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"]
//     .getService(Components.interfaces.nsIWindowWatcher);
//     var win = ww.openWindow(null,
// 			    "chrome://rcache/content/rcache_collector.xul", 
//     			    "status", 
//     			    "chrome,resizable", null);
//     return win;
//   }
// };

// //OLD STUFF
// //  reportHTML: function(){
// //     try{
// //       var win = this.window();
// //       //alert(win);
// //       var myreportdiv = win.document.createElement("DIV");
// //       myreportdiv.id = "rcache-report-div";
      
// //       var docul = win.document.createElement("UL");
// //       var pdful = win.document.createElement("UL");
// //       var matched_links = this.run();
// //       //alert(matched_links);

// //       for (var i = 0; i < matched_links['pdfs'].length; i++){
	
// // 	var pdfli = win.document.createElement("LI");
// // 	pdfli.innerHTML = matched_links['pdfs'][i].href;
// // 	pdful.appendChild(pdfli);
// //       }

// //       for (var i = 0; i < matched_links['docs'].length; i++){
// // 	var docli = win.document.createElement("LI");
// // 	docli.innerHTML = matched_links['docs'][i].href;
// // 	docul.appendChild(docli);
// //       }
// //       var anchor = win.document.createElement("A");
// //       anchor.name = "extractor-report";
// //       myreportdiv.appendChild(anchor);
// //       myreportdiv.appendChild(pdful);
// //       myreportdiv.appendChild(docul);

// //       var b = win.document.getElementsByTagName("BODY");
// //       var bdy = b.item(null);
// //       bdy.appendChild(myreportdiv);
// //     } catch(e){
// //       alert(e);
// //     }
// //   },
