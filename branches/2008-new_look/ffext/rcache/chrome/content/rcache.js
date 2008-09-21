// prototypes
Array.prototype.exists = function(o) {
  for(var i = 0; i < this.length; i++)
    if(this[i] === o)
      return true;
  return false;
};

var utils = {};
var debug = true;

Application.console.open();

var rc = {};

//rc.post_url = 'https://collect.rcache.com/postcache/?version=0.2.0';

rc.url = function(url_key){
  if (url_key === 'recent'){
    return 'https://collect.rcache.com/recent_xhr/?version=0.2.0&offset=1';
  } else if (url_key === 'post'){
    return 'https://collect.rcache.com/postcache/?version=0.2.0';
  } else if (url_key === 'colleagues'){
    return 'https://collect.rcache.com/xhr/colleagues/?version=0.2.0';
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

rc.toggle = function(){
  // open or close th UI

  var rc_ui = document.getElementById('rc-wrapper-box');
  if (rc_ui.hidden){
    rc_ui.hidden = false;
    rc.clean_up();
    rc.collect();
  } else {
    rc_ui.hidden = true;
  }
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
  for (var i = 0; i < lst_bx.getRowCount(); i++){
    lst_bx.removeItemAt(i);
  }
};

rc.clean_textboxes = function(){
  // clean all text boxes
  try{
    document.getElementById('url').value = '';
    document.getElementById('pagetitle').value = '';
    document.getElementById('tags').value = '';
    document.getElementById('selectedtext').value = '';
  } catch(e){
    rc.log(e);
  }
};

rc.clean_up = function(){
  // clean up the rc form, ready for a new cache
  try{
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
	  var timeout = window.setTimeout(rc.toggle, 1200);
	} else if (res === 'login_error'){
	  document.getElementById('cache-button').disabled = false;
	  document.getElementById('progress').hidden = true;
	  rc.message("Please Login to rCache");
	  window.open("https://collect.rcache.com/loginxul/",
	              "rcache-loginxul",
		      "menubar=no,location=no,resizable=no,scrollbars=yes,status=yes,width=400,height=210");
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
    rc.log("doc created: " + rc.document);
    rc.collector.selected_obj = wndw.getSelection();
    rc.log("window.getSelection() called");
    var selected_text = rc.collector.selected_obj.toString();
    rc.collector.src = selected_text;
    rc.log("selected text added to rc.collector.src");
    rc.log(rc.collector.src);
    //return selection;
  } catch (e){
    rc.log(e);
  }

};

rc.collector.src = null;
rc.collector.title = null;
rc.collector.url = null;
rc.collector.selection_obj= null;

rc.collector.make_frag = function(){
  //make the fragment object!
  try {
    //var sel = document.commandDispatcher.focusedWindow.getSelection();
    var sel = rc.collector.selected_obj;
    var rng = sel.getRangeAt(0);
    var frag = rng.cloneContents();
    rc.collector.src = sel.toString();
    var element = rc.document.createElement("div");
    element.id = "rcache-tmp-div";
    element.appendChild(frag);
    var doc_el = rc.document.getElementById('rcache-tmp-div');
    rc.log(doc_el);
    rc.log("src text: " + rc.collector.src);

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
    //sel.removeAllRanges();

  } catch(e){
    rc.log(e);
  }

};

rc.collector.links = [];
rc.collector.imgs = [];
rc.collector.media = [];

rc.collector.fill_form = function(){
  // fill out the collector form
  rc.log("starting fill_form function");
  var selTex = document.getElementById('selectedtext');
  rc.log(selTex);
  //selTex.setAttribute("value",rc.collector.src);
  selTex.value = rc.collector.src;
  rc.log("txt: " + rc.collector.src);
  rc.log("selectedtext content: " + selTex.value);
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
    try {
      var res = eval('(' + data + ')');
      rc.log("res: " + res.toString());
      if (res.entries_db.totalItems > 0){
	rc.log("total items: " + res.entries_db.totalItems);
	rc.log("first entry: " + res.entries_db.items[0].name);
	var tree = document.getElementById('rc-recent-tree-children');
	rc.log(tree.id);
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
      throw("Error: " + e);
    }

  });
};

rc.entries.remove_nodes = function(){
  // remove all nodes!!!
};

rc.entries.append_nodes = function(tree,rows){
  // fill the tree with rows
  rc.log("start append nodes");
  rc.log("rows.length: " + rows.length);
  for (var i=0; i < rows.length; i++) {
    //rc.log(i);
    var titem = document.createElement("treeitem");
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



















rc.log("rCache Started");
