var rcache={postUrl:"https://collect.rcache.com/postcache/",open:function(){
rcache_window=document.getElementById("rCacheToolbar");
rcache_window.hidden=false;
rcache.toolbarLoad();
},close:function(){
rcache_window=document.getElementById("rCacheToolbar");
rcache_window.hidden=true;
},urlRegex:new RegExp("([^:]*):(//)?([^/]*)"),collector_win:function(){
var ww=Components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(Components.interfaces.nsIWindowWatcher);
var _2=ww.openWindow(null,"chrome://rcache/content/rcache_status.xul","status","chrome,resizable",null);
return _2;
},current_selection:null,currentURL:function(){
return getBrowser().currentURI.spec;
},run:function(){
var u=rcache.currentURL();
var _4="https://collect.rcache.com/cache?url="+u;
rcache.loadtab(_4);
},loadtab:function(_5){
var _6=getBrowser().addTab(_5);
getBrowser().selectedTab=_6;
},selection:function(){
var _7=document.commandDispatcher.focusedWindow;
var _8=_7.getSelection();
return _8;
},getdoc:function(){
var _9=document.commandDispatcher.focusedWindow;
return _9;
},paste_selected:function(){
var _a=rcache.selection();
var _b=document.getElementById("selectedtext");
_b.setAttribute("value",_a);
},imgs:function(){
var _c=document.commandDispatcher.focusedWindow;
var _d=_c.document.getElementsByTagName("IMG");
return _d;
},thetitle:function(){
var _e=document.commandDispatcher.focusedWindow;
var _f=_e.document.title;
return _f;
},thedoc:function(){
return gBrowser.selectedBrowser.contentDocument;
},postit:function(){
var txt=rcache.selection();
if(txt!=""){
var _11=rcache.post_url(rcache.postUrl,txt);
}else{
alert("No Text is Selected");
}
},toolbarLoad:function(){
var txt=rcache.selection();
title=rcache.thetitle();
var _13=document.getElementById("selectedtext");
_13.setAttribute("value",txt);
var _14=document.getElementById("pagetitle");
_14.setAttribute("value",rcache.thetitle());
var _15=document.getElementById("url");
_15.setAttribute("value",rcache.currentURL());
},images:new Array(),confirm:function(){
var _16=new Array();
var _17=new Array();
try{
var txt=rcache.selection();
var rng=txt.getRangeAt(0);
var _1a=rng.cloneContents();
var _1b=content.document.createElement("DIV");
_1b.id="rcache-tmp-div";
_1b.appendChild(_1a);
var _1c=_1b.getElementsByTagName("A");
for(var i=0;i<_1c.length;i++){
_16.push(_1c[i].href);
}
}
catch(e){
}
try{
var txt=rcache.selection();
var rng=txt.getRangeAt(0);
var _1a=rng.cloneContents();
var _1b=content.document.createElement("DIV");
_1b.id="rcache-tmp-div-img";
_1b.appendChild(_1a);
var _1e=_1b.getElementsByTagName("IMG");
for(var i=0;i<_1e.length;i++){
_17.push(_1e[i].src);
}
}
catch(e){
}
if(txt!=""){
var _1f=rcache.thetitle();
var _20=rcache.collector_win();
var _21=function(){
var _22=_20.document.getElementById("selectedtext");
_22.setAttribute("value",txt);
var _23=_20.document.getElementById("pagetitle");
_23.setAttribute("value",rcache.thetitle());
var _24=_20.document.getElementById("url");
_24.setAttribute("value",rcache.currentURL());
var _25=_20.document.getElementById("linkbox");
for(var i=0;i<_16.length;i++){
_25.appendItem(_16[i]);
}
var _27=_20.document.getElementById("imgbox");
for(var i=0;i<_17.length;i++){
_27.appendItem(_17[i]);
}
};
_20.addEventListener("load",_21,false);
}else{
alert("rCache: Please highlight a portion of this page.");
}
},post_after_confirm:function(){
var _28=false;
setInterval(rcache.evalComplete,100);
rcache.http_collector();
},http_collector:function(){
if(document.getElementById("selectedtext").value!=""){
var _29=rcache.postUrl;
var _2a=new XMLHttpRequest();
var _2b=document.getElementById("url").value;
var _2c="entry_url="+encodeURIComponent(_2b)+"&";
var _2d=document.getElementById("pagetitle").value;
var _2e="entry_name="+encodeURIComponent(_2d)+"&";
var _2f=document.getElementById("pagetitle").value;
var _30="description="+encodeURIComponent(_2f)+"&";
var _31=document.getElementById("selectedtext").value;
var _32="text_content="+encodeURIComponent(_31)+"&";
var _33=document.getElementById("tags").value;
var _34="tags="+encodeURIComponent(_33)+"&";
var _35="links_qs"+"=";
try{
var _36=document.getElementById("linkbox");
_36.selectAll();
if(_36.selectedCount>0){
var _37=new Array();
for(var i=0;i<_36.selectedCount;i++){
var _39=_36.selectedItems[i].label;
_37.push(_39);
}
var _35=_35+_37.join("||sep||");
}
}
catch(e){
}
var _3a="imgs_qs"+"=";
try{
var _3b=document.getElementById("imgbox");
_3b.selectAll();
if(_3b.selectedCount>0){
var _3c=new Array();
for(var i=0;i<_3b.selectedCount;i++){
var _39=_3b.selectedItems[i].label;
_3c.push(_39);
}
_3a=_3a+_3c.join("||sep||");
}
}
catch(e){
}
_35=_35+"&";
var _3d=_2c+_2e+_30+_32+_34+_35+_3a;
_2a.onreadystatechange=function(){
if(_2a.status==200){
if(_2a.readyState==4){
if(eval(_2a.responseText)=="done"){
document.getElementById("progress").hidden=true;
bCompleted=true;
}else{
if(eval(_2a.responseText)=="login_error"){
document.getElementById("cache-button").disabled=false;
document.getElementById("progress").hidden=true;
window.open("https://collect.rcache.com/loginxul/","rcache-loginxul","menubar=no,location=no,resizable=no,scrollbars=yes,status=yes,width=348,height=195");
bCompleted=false;
}else{
document.getElementById("cache-button").disabled=false;
alert(_2a.responseText);
}
}
}
}else{
bCompleted=false;
document.getElementById("cache-button").disabled=false;
alert(_2a.responseText);
}
};
document.getElementById("progress").hidden=false;
document.getElementById("cache-button").disabled=true;
_2a.open("POST",_29,true);
_2a.setRequestHeader("Content-type","application/x-www-form-urlencoded");
_2a.setRequestHeader("Content-length",_3d.length);
_2a.setRequestHeader("Connection","close");
_2a.send(_3d);
}else{
alert("No Text is Selected");
return false;
}
},statusMsg:function(){
window.document.getElementById("statusmsg").value="Sucessful rCache.";
},evalComplete:function(){
if(bCompleted==true){
bCompleted=false;
window.setInterval(rcache.statusMsg,100);
window.setInterval(window.close,1200);
}
},winclose:function(){
self.close();
},post_url:function(url,_3f){
var _40=new XMLHttpRequest();
var _41="entry_url="+encodeURIComponent(rcache.currentURL())+"&";
var _42="entry_name="+encodeURIComponent(rcache.thetitle())+"&";
var _43="description="+encodeURIComponent(rcache.thetitle())+"&";
var _44="text_content="+encodeURIComponent(_3f);
var _45=_41+_42+_43+_44;
_40.open("POST",url,true);
_40.setRequestHeader("Content-type","application/x-www-form-urlencoded");
_40.setRequestHeader("Content-length",_45.length);
_40.setRequestHeader("Connection","close");
_40.onreadystatechange=function(){
if(_40.readyState==4&&_40.status==200){
alert(_40.responseText);
}
};
_40.send(_45);
},items_by_tag:function(tag){
var _47=browser.contentWindow.document.getElementsByTagName(tag);
var _48=[];
for(var i=0;i<_47.length;i++){
var img=_47.pop().toString();
_48.concat(img);
}
return _48;
},view_img_as_string:function(){
var _4b=rcache.items_by_tag("img");
alert(_4b[0]);
},view_img_test:function(){
var _4c=browser.contentWindow.document.getElementsByTagName("td");
alert(_4c[0].toString());
},append_list_item:function(_4d){
var _4e=document.getElementById("recent-listbox");
_4e.appendItem(_4d);
},append_list_items:function(){
var _4f=["test me indeed","test2 indeed","test3 is the best","test4 totally rocks"];
for(var i=0;i<_4f.length;i++){
rcache.append_list_item(_4f[i]);
}
},get_latest_entries:function(){
},append_links:function(_51,_52){
_52.appendItem("this is a test");
},latest_entries:function(url){
var _54=new XMLHttpRequest();
_54.open("GET","http://127.0.0.1:8000/recent_xhr/",true);
_54.onreadystatechange=function(){
if(_54.status==200){
if(_54.readyState==4){
bCompleted=true;
var res=eval(_54.responseText);
if(res.status=="success"){
bCompleted=true;
}else{
bCompleted=false;
}
}
}
};
_54.send(null);
},test_browser:function(){
var _56=window.document.getElementById("collector-iframe");
var _57=_56.rcache-collector;
}};
var fragmentMiner={processLinks:function(_58){
var _59=fragmentMiner.makeFrag(_58);
var _5a=fragmentMiner.makeElement(_59);
var _5b=fragmentMiner.getLinks(_5a);
return _5b;
},processImageSrc:function(_5c){
var _5d=fragmentMiner.makeFrag(_5c);
var _5e=fragmentMiner.makeElement(_5d);
var _5f=fragmentMiner.getImgs(_5e);
return _5f;
},makeFrag:function(_60){
var rng=_60.getRangeAt(0);
var _62=rng.cloneContents();
return _62;
},makeElement:function(_63){
var d=document.createElement("DIV");
d.appendChild(_63);
return d;
},getLinks:function(_65){
var _66=new Array();
var _67=_65.getElementsByTagName("A");
for(var i=0;i<_67.length;i++){
_66.push(_67[i].href);
}
return _66;
},getImgs:function(_69){
var _6a=new Array();
var _6b=_69.getElementsByTagName("IMG");
for(var i=0;i<_6b.length;i++){
if(_6b[i].src){
_6a.push(links[i].src);
}
}
return _6a;
},fetchImg:function(url){
var _6e=new XMLHttpRequest();
_6e.onreadystatechange=function(){
if(_6e.status==200){
fragmentMiner.imgStore.push(_6e.responseText);
if(_6e.readyState==4){
var res=_6e.responseText;
}
}
};
_6e.open("GET",url,false);
_6e.send(null);
},imgStore:new Array(),fetchImgs:function(_70){
for(i=0;i<_70.length;i++){
var img=fragmentMiner.fetchImg(_70[i]);
}
return fragmentMiner.imgStore;
}};

