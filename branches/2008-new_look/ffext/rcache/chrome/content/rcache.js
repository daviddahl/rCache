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

var rc = function(){
};

rc.log = function(msg){
  // log stuff to error console
  try{
    Application.console.log(msg);
  } catch(e){
    // noop
  }
};

rc.start = function(){
  // start it up beyotch
};

rc.toggle = function(){
  // open or close th UI

  var rc_ui = document.getElementById('rc-wrapper-box');
  if (rc_ui.hidden){
    rc_ui.hidden = false;
  } else {
    rc_ui.hidden = true;
  }
};

rc.post = function(){
  // send it all to the server!
  alert("POST it");

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

  rc.collector.select();
  rc.collector.make_frag();
  rc.collector.fill_form();

};

rc.collector = function(){
  // collector namespace
};

rc.document = null;

rc.collector.select = function(){
  rc.log("select called");
  var wndw = document.commandDispatcher.focusedWindow;
  rc.log("wndw created");
  rc.log(wndw);
  rc.document = document.commandDispatcher.focusedWindow.document;
  rc.log("doc created");
  rc.log(rc.document);
  try{
    rc.collector.selection_obj = document.commandDispatcher.focusedWindow.getSelection();
    var selected_text = rc.collector.selection_obj.toString();
    rc.collector.src = selected_text;
    rc.log("selected text added to rc.collector.src");
    rc.log(rc.collector.src);
  } catch (e){
    rc.log(e);
    return;
  }

};

rc.collector.src = null;
rc.collector.title = null;
rc.collector.url = null;
rc.collector.selection_obj= null;

rc.collector.make_frag = function(){
  //make the fragment object!
  try{
    var rng = rc.collector.selection_obj.getRangeAt(0);
    var frag = rng.cloneContents();
    var element = rc.document.createElement("div");
    element.id = "rcache-tmp-div";
    element.appendChild(frag);

    var linkObjs = element.getElementsByTagName("a");
    for (var i = 0; i < linkObjs.length; i++){
      if (!rc.collector.links.exists(linkObjs[i].href)){
	rc.collector.links.push(linkObjs[i].href);
      }
    }

    var imgObjs = element.getElementsByTagName("img");
    for (var j = 0; j < imgObjs.length; j++){
      if(!rc.collector.imgs.exists(linkObjs[j].href)){
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
  try{

    var selTex = document.getElementById('selectedtext');
    selTex.setAttribute("value",rc.collector.src);

    var pgTitle = document.getElementById('pagetitle');
    pgTitle.setAttribute("value",rc.collector.title);

    var pgUrl = document.getElementById('url');
    pgUrl.setAttribute("value",rc.collector.url);

    var linksLst = document.getElementById('linkbox');

    for (var i = 0; i < rc.collector.links.length; i++){
      linksLst.appendItem(rc.collector.links[i]);
    }

    var imgLst = document.getElementById('imgbox');
    for (var j = 0; j < rc.collector.imgs.length; j++){
      imgLst.appendItem(rc.collector.imgs[j]);
    }

  } catch(e){

    rc.log(e);

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


rc.log("rCache Started");
