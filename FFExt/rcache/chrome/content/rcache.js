var rcache = {
  postUrl: 'https://collect.rcache.com/postcache/',
  //postUrl: 'http://127.0.0.1:8000/postcache/',

 open: function(){
    rcache_window = document.getElementById('rCacheToolbar');
    rcache_window.hidden = false;
    //fixme: set pref to not run the load routine if so desired by user
    rcache.toolbarLoad();
  },
 close: function(){
    rcache_window = document.getElementById('rCacheToolbar');
    //fixme: check for un-cached data b4 closing??
    rcache_window.hidden = true;
  },
 urlRegex: new RegExp("([^:]*):(//)?([^/]*)"),

 collector_win: function(){
    var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"]
    .getService(Components.interfaces.nsIWindowWatcher);
    var win = ww.openWindow(null,"chrome://rcache/content/rcache_status.xul", 
    			    "status", 
    			    "chrome,resizable", null);
    return win;
  },

 current_selection: null,

 currentURL: function(){
    return getBrowser().currentURI.spec;
  },

 run: function(){
    var u = rcache.currentURL();
    var url = 'https://collect.rcache.com/cache?url='+ u;
    rcache.loadtab(url);
  },

 loadtab: function(url){
    var tab = getBrowser().addTab( url );
    getBrowser().selectedTab = tab; 
  },

 selection: function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var selected_txt=wndw.getSelection();
    return selected_txt;
  },

 getdoc: function(){
    var doc = document.commandDispatcher.focusedWindow;
    return doc;
  },

 paste_selected: function(){
    var txt = rcache.selection();
    var selTex = document.getElementById('selectedtext');
    selTex.setAttribute("value",txt);
  },

 imgs: function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var images=wndw.document.getElementsByTagName("IMG");
    return images;
  },

 thetitle: function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var title=wndw.document.title;
    return title;
  },
 
 thedoc: function(){
    return gBrowser.selectedBrowser.contentDocument;
  },

 postit: function(){
    //check selected text here to kill off connection from the start
    var txt = rcache.selection();
    //alert(txt);
    if (txt !=""){
      var result = rcache.post_url(rcache.postUrl,txt);
      //fixme: need callback to notify when done... 
    } else {
      alert("No Text is Selected");
    }
  },

 toolbarLoad: function(){
    var txt = rcache.selection();
    title = rcache.thetitle();
    var selTex = document.getElementById('selectedtext');
    selTex.setAttribute("value",txt);
    var pgTitle = document.getElementById('pagetitle');
    pgTitle.setAttribute("value",rcache.thetitle());
    var pgUrl = document.getElementById('url');
    pgUrl.setAttribute("value",rcache.currentURL());
  },

 images: new Array(),

 confirm: function(){
    var links = new Array();
    var imgs = new Array();
    //get a hrefs
    try{
      var txt = rcache.selection();
      var rng = txt.getRangeAt(0);
      var frag = rng.cloneContents();
      var element = content.document.createElement("DIV");    
      element.id = "rcache-tmp-div";
      element.appendChild(frag);
      var linkObjs = element.getElementsByTagName("A");
      for (var i = 0; i < linkObjs.length; i++){
	links.push(linkObjs[i].href);
      }
    } catch(e){
      //alert(e);
      //silently pass
    }
    //get img src strings
    try{
      var txt = rcache.selection();
      var rng = txt.getRangeAt(0);
      var frag = rng.cloneContents();
      var element = content.document.createElement("DIV");    
      element.id = "rcache-tmp-div-img";
      element.appendChild(frag);
      var imgObjs = element.getElementsByTagName("IMG");
      for (var i = 0; i < imgObjs.length; i++){
	imgs.push(imgObjs[i].src);
      }
    } catch(e){
      //alert(e);
      //silently pass
    }

    if (txt !=""){
      var title = rcache.thetitle();
      var confirmwin = rcache.collector_win();
      //var progress = confirmwin.document.getElementById('progress');
      //progress.hidden = false;
      var loadFunction = function() {
	var selTex =
	confirmwin.document.getElementById('selectedtext');
	selTex.setAttribute("value",txt);
	var pgTitle =
	confirmwin.document.getElementById('pagetitle');
	pgTitle.setAttribute("value",rcache.thetitle());
	var pgUrl =
	confirmwin.document.getElementById('url');
	pgUrl.setAttribute("value",rcache.currentURL());

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
  },
 
 post_after_confirm: function(){
    var bCompleted = false;
    setInterval(rcache.evalComplete, 100);
    rcache.http_collector();
  },
 
 http_collector: function(){
    if (document.getElementById('selectedtext').value !=""){
      var serverurl = rcache.postUrl;
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
	      bCompleted = true;
	    }
	    else if(eval(http.responseText) == 'login_error'){
	      //var wintext = document.getElementById('progress').hidden = true;
	      alert("Login Required.\n\nIn your browser, go to https://rcache.com/login/ \n\nLogin to rCache, and you'll be all set.");
	      bCompleted = false;
	    } else {
	      //no idea what is what??
	      alert(http.responseText);
	    }
	  }
	} else {
	  bCompleted = false;
	  alert(http.responseText);
	}
      }
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
  },
 
 statusMsg: function(){
    window.document.getElementById('statusmsg').value = "Sucessful rCache.";
  },

 evalComplete: function(){
    if (bCompleted == true) {
      bCompleted = false;
      window.setInterval(rcache.statusMsg, 100);
      window.setInterval(window.close, 1200);
    }
  },

 winclose: function(){
    self.close();
  },

 post_url: function(url,post_data){
    var http = new XMLHttpRequest();
    var link = 'entry_url=' + encodeURIComponent(rcache.currentURL()) + '&';
    var name = 'entry_name=' + encodeURIComponent(rcache.thetitle()) + '&';
    var desc = 'description=' + encodeURIComponent(rcache.thetitle()) + '&';
    var text = 'text_content=' + encodeURIComponent(post_data);
    var params = link + name + desc + text; 
    //alert(params);
    http.open("POST", url, true);
    //Send the proper header infomation along with the request
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.setRequestHeader("Content-length", params.length);
    http.setRequestHeader("Connection", "close");
    http.onreadystatechange = function() {
      //Call a function when the state changes.
      if(http.readyState == 4 && http.status == 200) {
	alert(http.responseText);
	//need to just pass here...
      }
    }
    http.send(params);
  },

 items_by_tag: function(tag){
    var itms = browser.contentWindow.document.getElementsByTagName(tag);
    var itm_lst = [];
    for (var i = 0; i < itms.length; i++){
      var img = itms.pop().toString();
      itm_lst.concat(img);
    }
    return itm_lst;
  },

 view_img_as_string: function(){
    var imgs = rcache.items_by_tag('img');
    alert(imgs[0]);
  },

 view_img_test: function(){
    var itms = browser.contentWindow.document.getElementsByTagName('td');
    alert(itms[0].toString());
  },

 append_list_item: function(item){
    var listbx = document.getElementById('recent-listbox');
    listbx.appendItem(item);
    //listbx.appendItem(thetitle);
    
  },
 
 append_list_items: function(){

    var items = ["test me indeed","test2 indeed","test3 is the best","test4 totally rocks"];

    for (var i = 0; i < items.length; i++){
      rcache.append_list_item(items[i]);
    }
    //create a for loop here to populate listbox with most recent 10 entries
    
  },
 
 get_latest_entries: function(){
    //read http://rcache.com/ten_latest/
    //var tenlatest = eval(text);
    //return tenlatest
  },

 append_links: function(links,linksLst){
    linksLst.appendItem("this is a test");
  },

 latest_entries: function(url){
    var http = new XMLHttpRequest();
    http.open("GET", "http://127.0.0.1:8000/recent_xhr/", true);
    http.onreadystatechange = function() {
	//Call a function when the state changes.
	if(http.status == 200) {
	  if(http.readyState == 4){
	    bCompleted = true;
	    //fixme: responsText is never evaluated correctly here
	    var res = eval(http.responseText);
	    //alert(res);
	    if (res.status == 'success'){
	      bCompleted = true;
	    } else {
	      bCompleted = false;
	    }
	  }
	}
      }
    http.send(null);
  },

 test_browser: function(){
    var rBrsr = window.document.getElementById('collector-iframe');
    //alert(rBrsr);
    var rcClltr = rBrsr.rcache-collector;
    //alert(rcClltr);
    //alert(rcClltr.url.value);
  }



 //============> TODO <==============\\
 // 2. get list of images on page, any image over THRESHOLD xy gets pushed up to media table for entry
 // 3. Collect other data in html source: Metatags, etc...
 // 5. clipboard support in client
 // 6. HTML clipboard support in client - also how do you store that? are the images inline?
 // 7. parser for HTML clipboard stuff - parse all tags, links, etc
 // 8. Authentication on server
 //    Replicate TG rcache tools/interfaces    
 // 9. prefs.js!!! Prefs interface
 // 10. download and cache PDF, Word, Excel???

 //end of object
};

//utilities for DOM extraction, etc...
var fragmentMiner = {
 
  //get images and links from a Selection Object

 processLinks: function(selection){
    //public interface to get 'a hrefs' from selection as array
    var frag = fragmentMiner.makeFrag(selection);
    var element = fragmentMiner.makeElement(frag);
    var links = fragmentMiner.getLinks(element);
    return links;
  },

 processImageSrc: function(selection){
    //public interface to get img src from selection as array
    var frag = fragmentMiner.makeFrag(selection);
    var element = fragmentMiner.makeElement(frag);
    var imgs = fragmentMiner.getImgs(element);
    return imgs;
    //still need to get each image via XMLHttpRequest: see fetchImg()
  },

 makeFrag: function(selection){
    var rng = selection.getRangeAt(0);
    var clone = rng.cloneContents();
    return clone;
  },
 
 makeElement: function(fragment){
    //wrap the fragment object in a Div to use HTMLElement methods on it!
    var d = document.createElement("DIV");
    d.appendChild(fragment);
    return d;
  },

 getLinks: function(element){
    var lnkArr = new Array();
    var links = element.getElementsByTagName("A");
    for (var i = 0; i < links.length; i++){
	lnkArr.push(links[i].href);
    }
    return lnkArr;
  },
 
 getImgs: function(element){
    var imgArr = new Array();
    var imgs = element.getElementsByTagName("IMG");
    for (var i = 0; i < imgs.length; i++){
      if (imgs[i].src){
	imgArr.push(links[i].src);
      }
    }
    return imgArr;
  },
 
 fetchImg: function(url){
    var http = new XMLHttpRequest();
    http.onreadystatechange = function() {
      //Call a function when the state changes.
      if(http.status == 200) {
	//might have to get img data here

	fragmentMiner.imgStore.push(http.responseText);

	if(http.readyState == 4){
	  var res = http.responseText;
	}
      }
    }
    http.open("GET", url, false);
    http.send(null);
  },
 
 imgStore: new Array(),

 fetchImgs: function(img_arr){
    for (i=0; i < img_arr.length; i++){
      //get img data via XMLHttpRequest
      var img = fragmentMiner.fetchImg(img_arr[i]);
     }
    return fragmentMiner.imgStore;
  }

};
