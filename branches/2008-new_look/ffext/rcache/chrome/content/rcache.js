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

rc.collector = function(){
  // collector namespace
};

rc.collector.url_check = function(){
  // check if the url has been colelcted and when -
  // show the current data in the database
};

rc.collector.bookmark_this = function(){
  // add the current url to the bookmarks with tags
};


rc.log("rCache Started");
