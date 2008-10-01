// rCache Collector 0.2.0
// Firefox extension - companion to rCache.com research tools
// Copyright, 2007, 2008 David L Dahl

// prototypes
Array.prototype.exists = function(o) {
  for(var i = 0; i < this.length; i++)
    if(this[i] === o)
      return true;
  return false;
};

var utils = {};

var debug = true;

try {
  Application.console.open();
} catch(e){
  //noop
}

var rc = {};

rc.version = '0.2.0';

rc.minimal_mode = false;

// todo: show minimal mode UI instead of standard UI
// minimal mode has only the title, tags, btn and progress elements visible

rc.minimal_ui = function(){
  // hide rc-wrapper-box, show rc-minimal-status-bar
};

rc.base_url = 'https://collect.rcache.com';
//rc.base_url = 'http://127.0.0.1:8000';

rc.url = function(url_key,id){

  if (url_key === 'recent'){
    return rc.base_url + '/recent_xhr/?version=0.2.0&offset=1';
  } else if (url_key === 'post'){
    return rc.base_url + '/postcache/?version=0.2.0';
  } else if (url_key === 'colleagues'){
    return rc.base_url + '/colleagues/?version=0.2.0';
  } else if (url_key === 'detail'){
    var u = rc.base_url + '/detail/' + id + '/?format=json&version=0.2.0';
    return u;
  } else {
    throw("rCache Error: Url is not defined, cannot complete request.");
  }

};

rc.log = function(msg){
  // log stuff to error console
  try{
    Application.console.log(msg);
  } catch(e){
    // noop
  }
};

rc.toggle = function(action){
  // open or close th UI
  var rc_ui = document.getElementById('rc-wrapper-box');
  if (action === 'collect'){
    if (rc_ui.hidden){
      rc_ui.hidden = false;
      rc.clean_up();
      rc.collect();
    } else {
      rc_ui.hidden = true;
    }
  } else {
     if (rc_ui.hidden){
      rc_ui.hidden = false;
      rc.clean_up();
     }
  }
  // select the right tab:
  var id = 'rc-tabs';
  var tab_box = document.getElementById(id);
  if (action === 'colleagues'){
    tab_box.selectedIndex = 2;
  }
  if (action === 'recent'){
    tab_box.selectedIndex = 1;
  }
  if (action === 'collect'){
    tab_box.selectedIndex = 0;
  }

};

rc.close = function(){
  // close the UI
  var rc_ui = document.getElementById('rc-wrapper-box');
  rc_ui.hidden = true;
  rc.document.body.focus();
};


rc.payload = null;

rc.window_context = null;

rc.make_post_obj = function(){
  rc.log(document.getElementById('selectedtext'));
  if (document.getElementById('selectedtext').value !==""){
    var post = {};
    var winurl = document.getElementById('url').value;
    post.entry_url = encodeURIComponent(winurl);
    var wintitle = document.getElementById('pagetitle').value;
    post.entry_name = encodeURIComponent(wintitle);
    var windesc = document.getElementById('pagetitle').value;
    post.description = encodeURIComponent(windesc);
    var wintext = document.getElementById('selectedtext').value;
    post.text_content = encodeURIComponent(wintext);
    var wintags = document.getElementById('tags').value;
    post.tags = encodeURIComponent(wintags);
    post.links_qs = '';
    post.html_content = rc.iframe;
    try {
      var lnkBx = document.getElementById('linkbox');
      lnkBx.selectAll();
      if (lnkBx.selectedCount > 0){
	var links = [];
	for (var i=0;i < lnkBx.selectedCount; i++){
	  var item = lnkBx.selectedItems[i].label;
	  links.push(item);
	}
	post.links_qs = post.links_qs + links.join("||sep||");
      }
    } catch(e) {
      rc.log(e);
    }
    post.imgs_qs = '';
    try {
      var imgBx = document.getElementById('imgbox');
      imgBx.selectAll();
      if (imgBx.selectedCount > 0){
	var imgs = [];
	for (var i=0;i < imgBx.selectedCount; i++){
	  var item = imgBx.selectedItems[i].label;
	  imgs.push(item);
	}
	post.imgs_qs = post.imgs_qs + imgs.join("||sep||");
      }
    } catch(e) {
      rc.log(e);
    }
    rc.payload = post;
  } else {
    alert("rCache: No Text is Selected");
  }
};

rc.message = function(msg){
  document.getElementById('statusmsg').value = msg;
};

rc.clean_listbox = function(id){
  var lst_bx = document.getElementById(id);
  while (lst_bx.hasChildNodes()) {
    lst_bx.removeChild(lst_bx.childNodes[0]);
  }
};

rc.clean_textboxes = function(){
  // clean all text boxes
  try {
    document.getElementById('url').value = '';
    document.getElementById('pagetitle').value = '';
    document.getElementById('tags').value = '';
    document.getElementById('selectedtext').value = '';
  } catch(e) {
    rc.log(e);
  }
};

rc.clean_up = function(){
  // clean up the rc form, ready for a new cache
  try {
    var src_tabs = document.getElementById('rc-page-frag');
    src_tabs.selectedIndex = 0;
    var ifrm = document.getElementById('rc-iframe');
    ifrm.parentNode.removeChild(ifrm);
    rc.payload = null;
    rc.message("Ready.");
    rc.document = null;
    rc.collector.src = null;
    rc.collector.title = null;
    rc.collector.url = null;
    rc.collector.selection_obj= null;
    rc.collector.links = [];
    rc.collector.imgs = [];
    rc.collector.media = [];

    rc.clean_listbox('linkbox');
    rc.clean_listbox('imgbox');
    rc.clean_listbox('mediabox');
    rc.clean_textboxes();

  } catch(e){
    rc.log(e);
  }

};

rc.login = function(){
  window.open(rc.base_url + "/loginxul/",
	      "rcache-loginxul",
	      "menubar=no,location=no,resizable=no,scrollbars=yes,status=yes,width=400,height=210");
};

rc.post = function(){
  // POST it to the server!
  try{
    rc.make_post_obj();
  } catch(e){
    rc.log(e);
  }

  // sanity check and post it!
  if (rc.payload){
    try {
      document.getElementById('cache-button').disabled = true;
      document.getElementById('progress').hidden = false;
      $.post(rc.url('post'),rc.payload,function(data){
	var res = eval(data);
	if (res === 'done'){
	  // show message, re-initialize rc
	  document.getElementById('cache-button').disabled = false;
	  document.getElementById('progress').hidden = true;
	  rc.message("Successful rCache.");
	  // clean out the rCache form
	  //rc.clean_up();
	  // need a 2 second timer here
	  var timeout = window.setTimeout(rc.close, 1200);
	} else if (res === 'login_error'){
	  document.getElementById('cache-button').disabled = false;
	  document.getElementById('progress').hidden = true;
	  rc.message("Please Login to rCache");
	  rc.login();
	} else {
	  // huh? throw an exception...
	  document.getElementById('cache-button').disabled = false;
	  document.getElementById('progress').hidden = true;
	  rc.message("Transmission Error");
	  //alert("rCache: Transmission Error.");
	}
      });
    } catch(e){
      rc.log(e);
      document.getElementById('cache-button').disabled = false;
      document.getElementById('progress').hidden = true;
      alert("rCache: Transmission Error. Exception Thrown.: " + e);
    }

  } else {
    alert("rCache: Click on the Collect button first.");
  }
};

rc.ui = function(){
  // handle UI changes, toggling between entries and collector
};

rc.ui.collector = function(){
  // show the collector UI
};

rc.ui.entries = function(){
  // show the entries UI
};

rc.ui.help  = function(){
  // show the help pages
};

rc.ui.new_install = function(){
  // show the UI that introduces a new user to rCache
};

rc.collect = function(){
  // do the page scrape here!
  try{
    var tab_box = document.getElementById('rc-tabs');
    tab_box.selectedIndex = 0;
    rc.collector.select();
    rc.collector.make_frag();
    rc.collector.fill_form();
  } catch(e) {
    rc.log(e);
  }

};

rc.collector = {};

rc.document = null;

rc.target_window = null;

rc.collector.select = function(){
  try {
    rc.log("select called");
    var wndw = document.commandDispatcher.focusedWindow;
    var focusedWindow = document.commandDispatcher.focusedWindow;
    var selection = focusedWindow.getSelection();
    rc.log("wndw created");
    rc.target_window = wndw;
    rc.document = document.commandDispatcher.focusedWindow.document;

    var src_el = rc.document.createElement("div");
    src_el.appendChild(wndw.getSelection().getRangeAt(0).cloneContents());
    rc.collector.html = src_el;
    rc.log("html: " + rc.collector.html);

    try {
      rc.style.make_iframe();
      rc.style.fill_iframe();
    } catch(e){
      rc.log(e);
    }
    //rc.log("doc created: " + rc.document);
    rc.collector.selected_obj = wndw.getSelection();
    //rc.log("window.getSelection() called");
    var selected_text = rc.collector.selected_obj.toString();
    rc.collector.src = selected_text;
    //rc.log("selected text added to rc.collector.src");
    //rc.log(rc.collector.src);
    //return selection;
  } catch (e){
    rc.log(e);
  }

};

rc.collector.html = null;

rc.collector.src = null;

rc.collector.title = null;

rc.collector.url = null;

rc.collector.selection_obj= null;

rc.collector.dom_nodes = null;

rc.collector.dom_list = [];

rc.collector.make_dom = function(){
  // take fragment and get all nodes as list
  try{
    for (var i = 0; i < rc.collector.dom_nodes.length; i++){
      rc.collector.dom_list.push(rc.collector.dom_nodes[i]);
      if (rc.collector.dom_nodes[i].childNodes){
	rc.collector.make_dom(rc.collector.dom_nodes[i]);
      }
    }
  } catch(e){
    rc.log(e);
  }

};

rc.collector.make_frag = function(){
  //make the fragment object!
  try {
    var sel = rc.collector.selected_obj;
    var rng = sel.getRangeAt(0);
    var frag = rng.cloneContents();
    rc.collector.dom_nodes = frag;
    rc.collector.make_dom();
    rc.collector.src = sel.toString();
    var element = rc.document.createElement("div");
    element.id = "rcache-tmp-div";
    element.appendChild(frag);
    var doc_el = rc.document.getElementById('rcache-tmp-div');
    //rc.log(doc_el);
    //rc.log("src text: " + rc.collector.src);

    var linkObjs = element.getElementsByTagName("a");
    for (var i = 0; i < linkObjs.length; i++){
      if (!rc.collector.links.exists(linkObjs[i].href)){
    	rc.collector.links.push(linkObjs[i].href);
      }
    }

    var imgObjs = element.getElementsByTagName("img");
    for (var j = 0; j < imgObjs.length; j++){
      if(!rc.collector.imgs.exists(imgObjs[j].href)){
    	rc.collector.imgs.push(imgObjs[j].src);
      }

    }
    // set the title and url as well:
    rc.collector.title = rc.document.title;
    rc.collector.url = rc.document.location.href;

  } catch(e){
    rc.log(e);
  }

};

rc.collector.links = [];
rc.collector.imgs = [];
rc.collector.media = [];

rc.collector.fill_form = function(){
  // fill out the collector form
  //rc.log("starting fill_form function");
  var selTex = document.getElementById('selectedtext');
  //rc.log(selTex);
  //selTex.setAttribute("value",rc.collector.src);
  selTex.value = rc.collector.src;
  //rc.log("txt: " + rc.collector.src);
  //rc.log("selectedtext content: " + selTex.value);
  var pgTitle = document.getElementById('pagetitle');
  pgTitle.value = rc.collector.title;

  var pgUrl = document.getElementById('url');
  pgUrl.value =rc.collector.url;

  var linksLst = document.getElementById('linkbox');

  for (var i = 0; i < rc.collector.links.length; i++){
    linksLst.appendItem(rc.collector.links[i]);
  }

  var imgLst = document.getElementById('imgbox');
  for (var j = 0; j < rc.collector.imgs.length; j++){
    imgLst.appendItem(rc.collector.imgs[j]);
  }

  // focus on tags!
  var tags = document.getElementById('tags');
  tags.focus();
  // now activate the 'rCache this' button

};

rc.collector.url_check = function(){
  // check if the url has been colelcted and when -
  // show the current data in the database
};

rc.collector.bookmark_this = function(){
  // add the current url to the bookmarks with tags
};

rc.upload = function(){
  // upload namespace for local file push tools
};

rc.upload.local_dir = null;

rc.upload.choose_local_dir = function(){
  // choose a local dir to push pdf's word ect from to rcache.com
};

rc.entries = {};

rc.entries.recent = function(){
  // get the recent entry objects from the server
  rc.log("Getting recent entries...");

  var url = rc.url('recent');
  rc.log(url);
  $.get(url,function(data){
    //var prog = document.getElementById('rc-entries-reload-progress');
    //prog.src = rc.spinner_on;
    try {
      var res = eval('(' + data + ')');
      if (res.entries_db.totalItems > 0){
	var tree = document.getElementById('rc-recent-tree-children');
	try{
	  rc.entries.append_nodes(tree,res.entries_db.items);
	} catch(e){
	  rc.log(e);
	}
      } else {
	alert("rCache: No entries found");
      }
    } catch(e){
      rc.log(e);
      throw new Error("Error: " + e);
    }

  });
};

rc.entries.empty_tree = function() {
  var tchildren = document.getElementById('rc-recent-tree-children');
  while(tchildren.hasChildNodes()) {
    tchildren.removeChild(tchildren.childNodes[0]);
  }
};

rc.spinner_on  = "chrome://rcache/content/loading_16.gif";
rc.spinner_off  = "chrome://rcache/content/notloading_16.png";

rc.entries.append_nodes = function(tree,rows){
  // fill the tree with rows
  //rc.log("start append nodes");
  //rc.log("rows.length: " + rows.length);
  // remove all existing children
  rc.entries.empty_tree();

  var detail_func = function(){
    try{
      var t = document.getElementById('rc-recent-entries');
      var si = t.selectedItems;
      rc.log(t);
      rc.log(si);
      rc.log(si[0]);
      var id = si[0].firstChild.firstChild.getAttribute('label');
      var url = rc.url('detail',id);
      window.open(url);
    } catch(e){
      rc.log('Error:' + e);
    }
  };

  tree.addEventListener('dblclick',detail_func,true);

  for (var i=0; i < rows.length; i++) {
    //rc.log(i);
    var titem = document.createElement("treeitem");
    titem.setAttribute('id',rows[i].rcacheid);
    var trow = document.createElement("treerow");


    // columns
    var id_cell = document.createElement("treecell");
    var title_cell = document.createElement("treecell");
    var date_cell = document.createElement("treecell");
    //
    id_cell.setAttribute("label",rows[i].rcacheid );
    title_cell.setAttribute("label",rows[i].name );
    date_cell.setAttribute("label",rows[i].date );
    //
    trow.appendChild(id_cell);
    trow.appendChild(title_cell);
    trow.appendChild(date_cell);
    trow.setAttribute('hidden', false);
    //
    titem.appendChild(trow);
    titem.setAttribute('hidden', false);
    tree.appendChild(titem);
  }
};

rc.entries.detail = function(){
  // get the entry's details from the server
  var t = document.getElementById('rc-recent-entries');
  var idx = 0;
  var id = t.view.getCellText(t.currentIndex,t.columns.getColumnAt(idx));
  rc.log(id);
  // get the details from the server
  $.get(rc.url('detail',id),function(data){
      var res = JSON.parse(data);
      if (res.status === 'success'){
	document.getElementById('rc-entry-title').value = res.title;
	document.getElementById('rc-entry-tags').value = res.tags;
	//rc.log(res.entry_text);
	document.getElementById('rc-entry-text').value = res.entry_text;
      } else {
	rc.log(res.msg)
      }
    });
};

// style extraction and viewing namespace
rc.style = {};

rc.style.rules = [];

rc.style.style_tag_rules = '';

rc.style.get_rules = function(){
  // get all style rules for a page, save in rc.style.rules
  for (var i = 0; i < rc.document.styleSheets.length; i++){
    var sheet = rc.document.styleSheets[i];
    try{
      for (var j = 0; j < sheet.cssRules.length; j++){
	rc.style.rules.push(sheet.cssRules[j].cssText);
      }
      var style_objs = rc.document.getElementsByTagName('style');
      for (var k = 0; k < style_objs.length; k++){
	rc.style.style_tag_rules = rc.style.style_tag_rules +
	  style_objs[k].innerHTML;
      }
    } catch(e){
      rc.log(e);
    }
  }
};

rc.style.fill_iframe = function(){
  // use data URI scheme for iframe source!
  var style_rules = '';
  for (var i=0; i < rc.style.rules.length;i++){
    style_rules = style_rules + rc.style.rules[i].toString();
  }
  style_rules = style_rules + rc.style.style_tag_rules;
  var ifrm_src = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"' +
  '        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' +
  '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">' +
  '<head>' +
  '<meta http-equiv="cache-control" content="no-cache"/>' +
  '<meta http-equiv="expires" content="MON, 22 JUL 2002 11:12:01 GMT"/>' +
  '<meta http-equiv="pragma" content="no-cache"/>' +
  '<style id="rc-iframe-css">' +
  style_rules +
  '</style>' +
  '<title></title>' +
  '</head>' +
  '<body>' +
  '<div id="rc-iframe-content">' +
  rc.collector.html.innerHTML +
  '</div>' +
  '</body>' +
  '</html>';
  var data_uri_start = 'data:text/html,';
  var src = data_uri_start + ifrm_src;
  rc.iframe = src;
  document.getElementById('rc-iframe').setAttribute('src',src);
};

rc.style.make_iframe = function(){
  // load iframe via chrome://url
  //document.getElementById('rc-page-frag').
  //  addEventListener('click',rc.style.fill_iframe,false);
  rc.style.get_rules();
  var frm = document.createElement('iframe');
  frm.setAttribute('id','rc-iframe');
  frm.setAttribute('src','');
  var vbox = document.getElementById('rc-rendered-dom');
  vbox.appendChild(frm);
};

rc.iframe_start =
  '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"' +
  '        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' +
  '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">' +
  '<head>' +
  '<meta http-equiv="cache-control" content="no-cache"/>' +
  '<meta http-equiv="expires" content="MON, 22 JUL 2002 11:12:01 GMT"/>' +
  '<meta http-equiv="pragma" content="no-cache"/>' +
  '<style id="rc-iframe-css"></style>' +
  '<title></title>' +
  '</head>' +
  '<body>' +
  '<div id="rc-iframe-content"></div>' +
  '</body>' +
  '</html>';

rc.iframe = '';
rc.iframe_inner_html = '';

rc.doc_html_open = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"' +
	  '        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' +
  '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">';

rc.doc_html_close = '</html>';

rc.iframe_src = function(){
  // get the entire html document source
  var src = rc.doc_html_open +
    rc.iframe_inner_html  +
    rc.doc_html_close;
  return src;
};

rc.media = {};

rc.media.list_urls = function(){
  // get all media urls that we care about from img src, embed tags
  // return a list []
};

rc.media.download_media = function(){
    // download a media object, store in this.downloaded_media() like so:
    // downloaded_media['url'] = {'url':url,'mime_type':mime_type,'size':size'}
    var lstbx = document.getElementById('imgbox');
    var url = lstbx.getSelectedItem(0);
    var progress = document.getElementById('media-dl-progress');
    progress.value = 0;
    try{
	var data = this.download(url.label);
	//var dl_obj = {'data':data,'url':url.label,'mime_type':mime_type};
	//this.media_catalog.push(dl_obj);
	//var dl_obj = null;
    } catch(e){
	rc.log(e);
    }

};

rc.media.download = function(){
  // do the download!
  try {
    var lstbx = document.getElementById('imgbox');
    var url = lstbx.getSelectedItem(0).label;
    var dl_desc = document.getElementById('rc-media-dl-desc');
    dl_desc.setAttribute("value","Downloading: " + url );

    var before = function(){
      this.onprogress = rc.media.on_progress;
    };

    var completed = function(data){
      document.getElementById('rc-media-dl-desc').value = 'Download Complete';
      rc.media.catalog.push({'data':data.responseText,'url':rc.media.current_url});
      var mediaLst = document.getElementById('mediabox');
      mediaLst.appendItem(rc.media.current_url);
    };
    rc.media.current_url = url;
    var o = { 'url':url,
	      type:'GET',
	      beforeSend:before,
	      dataType:'text',
	      complete:completed };
    var http = $.ajax(o);
  } catch (e) {
    rc.log(e);
  }
};

rc.media.on_progress = function(e){
  try {
    var progress = document.getElementById('rc-media-dl-progress');
    var percentComplete = (e.position / e.totalSize)*100;
    progress.value = percentComplete;
  } catch(e) {
    rc.log(e);
  }
};

rc.media.current_url = null;

rc.media.catalog = [];


rc.colleagues = {};

rc.colleagues.refresh = function(){
  // refresh the colleagues list
  rc.log("Getting recent entries...");

  var url = rc.url('colleagues');
  rc.log(url);
  $.get(url,function(data){
    try {

      rc.log(data);
      var res = eval('(' + data + ')');
      rc.log(res);
      var listbx = document.getElementById('rc-colleagues');
      rc.clean_listbox('rc-colleagues');
      rc.log(listbx);
      for (var i = 0; i < res.colleagues.length; i++){
	listbx.appendItem(res.colleagues[i].colleague);
      }
    } catch(e){
      rc.log(e);
      alert(e);
    }
  });
};

rc.log("rCache Started");
