var rcache = {
  // postUrl: 'http://zinn.ddahl.com:8000/postcache/',
 postUrl: 'https://collect.rcache.com/postcache/',

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
    //var win = ww.openWindow(null,"chrome://rcache/content/rcache_status.xul", 
    //			    "status", 
    //			    "chrome,width=500,height=230,modal=no", null);
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
    var url = 'http://zinn.ddahl.com:8000/cache?url='+ u;
    rcache.loadtab(url);
  },

 loadtab: function(url){
    var tab = getBrowser().addTab( url );
    getBrowser().selectedTab = tab; 
  },

 selection: function(){
    var wndw=document.commandDispatcher.focusedWindow;
    var selected_txt=wndw.getSelection();
    rcache.current_selection = window.getSelection();
    return selected_txt;

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
      var result = rcache.post_url(rcache.postUrl,txt);      //fixme: need callback to notify when done... 
    } else {
      alert("No Text is Selected");
    }
  },

 toolbarLoad: function(){
    var txt = rcache.selection();
    //if (txt !=""){
      title = rcache.thetitle();
      var selTex = document.getElementById('selectedtext');
      selTex.setAttribute("value",txt);
      var pgTitle = document.getElementById('pagetitle');
      pgTitle.setAttribute("value",rcache.thetitle());
      var pgUrl = document.getElementById('url');
      pgUrl.setAttribute("value",rcache.currentURL());
    //}
  },

 confirm: function(){
    var txt = rcache.selection();
    var frag = fragmentMiner.makeFrag(txt);
    var links = fragmentMiner.getAnchors(frag);
    var imgs = fragmentMiner.getImgSrc(frag);
    //alert(links);
    //alert(imgs);
    
    if (txt !=""){
      title = rcache.thetitle();
      var confirmwin = rcache.collector_win();
      //var progress = confirmwin.document.getElementById('progress');
      //progress.hidden = false;
      var loadFunction = function() {
	selTex =
	confirmwin.document.getElementById('selectedtext');
	selTex.setAttribute("value",txt);
	pgTitle =
	confirmwin.document.getElementById('pagetitle');
              pgTitle.setAttribute("value",rcache.thetitle());
	pgUrl =
	confirmwin.document.getElementById('url');
              pgUrl.setAttribute("value",rcache.currentURL());
      };
      confirmwin.addEventListener("load", loadFunction, false); 
    } else {
      //paste the clipboard into txt
      alert("No Text is Selected");
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
      var link = 'entry_url=' + escape(winurl) + '&';
      
      var wintitle = document.getElementById('pagetitle').value;
      var name = 'entry_name=' + escape(wintitle) + '&';

      var windesc = document.getElementById('pagetitle').value;
      var desc = 'description=' + escape(windesc) + '&';

      var wintext = document.getElementById('selectedtext').value;
      var text = 'text_content=' + escape(wintext) + '&';

      var wintags = document.getElementById('tags').value;
      var tags = 'tags=' + escape(wintags)

      var params = link + name + desc + text + tags;
      
      http.onreadystatechange = function() {
	//Call a function when the state changes.
	if(http.status == 200) {
	  if(http.readyState == 4){
	    bCompleted = true;
	    //fixme: responsText is never evaluated correctly here
	    //collector always returns a successful rcache
	    var res = eval(http.responseText);
	    //alert(res);
	    if (res.status == 'success'){
	      //var wintext = document.getElementById('progress').hidden = true;
	      bCompleted = true;
	    } else {
	      bCompleted = false;
	    }
	  }
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
      window.setInterval(window.close, 1500);
    }
  },

 winclose: function(){
    self.close();
  },

 post_url: function(url,post_data){
    var http = new XMLHttpRequest();
    var link = 'entry_url=' + escape(rcache.currentURL()) + '&';
    var name = 'entry_name=' + escape(rcache.thetitle()) + '&';
    var desc = 'description=' + escape(rcache.thetitle()) + '&';
    var text = 'text_content=' + escape(post_data);
    var params = link + name + desc + text; 
    alert(params);
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
    //    for (itm in items){
    //  rcache.append_list_item(itm);
    //}

    for (var i = 0; i < items.length; i++){
      rcache.append_list_item(items[i]);
    }
    //var item ="A title of an entry";
    //create a for loop here to populate listbox with most recent 10 entries
    
  },
 
 get_latest_entries: function(){
    //read http://rcache.com/ten_latest/
    //var tenlatest = eval(text);
    //return tenlatest
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
	    alert(res);
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
    alert(rBrsr);
    var rcClltr = rBrsr.rcache-collector;
    alert(rcClltr);
    alert(rcClltr.url.value);
  }



 //============> TODO <==============\\
 // 1. get list of links in selected text or list of links in document
 //    for upload to entry_urls
 // 2. get list of images on page, any image over THRESHOLD xy gets pushed up to media table for entry
 // 3. Collect other data in html source: Metatags, etc...
 // 4. Tag support on server
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

//string = document.referrer 

var fragmentMiner = {
 
 makeFrag: function(selection){
    var rng = selection.getRangeAt(0);
    var clone = rng.cloneContents();
    return clone;
  },

 getAnchors: function(fragment){
    //pass a fragment and tag to traverse to return an array of wanted tag data
    if (fragment.hasChildNodes() == true){
      var y = fragment.childNodes;
      var result = [];
      for (i=0;i<y.length;i++){
	if (y[i].nodeType!=3){
	  if (y[i].nodeName == 'A'){
	    result.push(y[i].href);
	  }
	  for (z=0;z<y[i].childNodes.length;z++){
	    if (y[i].childNodes[z].nodeType!=3){
	      if (y[i].childNodes[z].nodeName == 'A'){
		result.push(y[i].childNodes[z].href);
	      }
	    }
	  }
	}
      }
      //fixme: need to make all href's absolute
      return result;
    }
  }, 
    
 getImgSrc: function(fragment){
    //pass a fragment to traverse to return an array of wanted tag data
    if (fragment.hasChildNodes() == true){
      var y = fragment.childNodes;
      var result = [];
      for (i=0;i<y.length;i++){
	if (y[i].nodeType!=3){
	  if (y[i].nodeName == 'IMG'){
	    result.push(y[i].src);
	  }
	  for (z=0;z<y[i].childNodes.length;z++){
	    if (y[i].childNodes[z].nodeType!=3){
	      if (y[i].childNodes[z].nodeName == 'IMG'){
		result.push(y[i].childNodes[z].src);
	      }
	    }
	  }
	}
      }
      //fixme: need to make all src's absolute
      return result;
    }
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
