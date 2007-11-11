var rclip={paste:function(){
var _1=Components.classes["@mozilla.org/widget/clipboard;1"].getService(Components.interfaces.nsIClipboard);
if(!_1){
return false;
}
var _2=Components.classes["@mozilla.org/widget/transferable;1"].createInstance(Components.interfaces.nsITransferable);
if(!_2){
return false;
}
_2.addDataFlavor("text/unicode");
_1.getData(_2,_1.kGlobalClipboard);
var _3=new Object();
var _4=new Object();
_2.getTransferData("text/unicode",_3,_4);
if(_3){
_3=_3.value.QueryInterface(Components.interfaces.nsISupportsString);
}
if(_3){
pastetext=_3.data.substring(0,_4.value/2);
}
return pastetext;
},copy:function(_5){
var _6=_5;
var _7=Components.classes["@mozilla.org/supports-string;1"].createInstance(Components.interfaces.nsISupportsString);
if(!_7){
return false;
}
_7.data=_6;
var _8=Components.classes["@mozilla.org/widget/transferable;1"].createInstance(Components.interfaces.nsITransferable);
if(!_8){
return false;
}
_8.addDataFlavor("text/unicode");
_8.setTransferData("text/unicode",_7,_6.length*2);
var _9=Components.interfaces.nsIClipboard;
var _a=Components.classes["@mozilla.org/widget/clipboard;1"].getService(_9);
if(!_a){
return false;
}
_a.setData(_8,null,_9.kGlobalClipboard);
return true;
}};

