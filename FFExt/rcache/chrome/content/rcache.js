var rcache = {

 urlRegex: new RegExp("([^:]*):(//)?([^/]*)"),
 
 brWin: function getBrowserWindowObj(){
    var _fs=Components.classes["@mozilla.org/appshell/window-mediator;1"]
    .getService(Components.interfaces.nsIWindowMediator);
    var win=_fs.getMostRecentWindow("navigator:browser");
    return win;
  },

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
    var title=wndw.document.title;
    return selected_txt;
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
      var result = rcache.post_url('http://zinn.ddahl.com:8000/postcache/',txt);      //fixme: need callback to notify when done... 
    } else {
      alert("No Text is Selected");
    }
  },

 confirm: function(){
    var txt = rcache.selection();
    if (txt !=""){
      title = rcache.thetitle();
      var confirmwin = window.open("chrome://rcache/content/rcache_status.xul", 
				   "status", 
				   "chrome,width=500,height=170,modal=no" );
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
      alert("No Text is Selected");
    }
  },

 post_after_confirm: function(){
    //tags not supported on server yet
    if (document.getElementById('selectedtext').value !=""){
      var serverurl = 'http://zinn.ddahl.com:8000/postcache/';
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
	if(http.readyState == 4 && http.status == 200) {
	  alert(http.responseText);
	  window.close();
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
    }
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
 
 status: function(){
    window.open("chrome://rcache/content/rcache_status.xul", "bmarks", "chrome,width=300,height=200");
  }
 //============> TODO <==============\\
 // 0. Open new tab after async http call to detail screen of 
 //    new rcache entry
 // 1. get list of links in selected text or list of links in document
 //    for upload to entry_urls
 // 2. get list of images on page, any image over THRESHOLD xy gets pushed up to media table for entry
 // 3. Collect other data in html source: Metatags, etc...
 // 


 //end of object
};

