//http://developer.mozilla.org/en/docs/Using_the_Clipboard
var rclip = {

 paste: function(){
    var clip  = Components.classes["@mozilla.org/widget/clipboard;1"].getService(Components.interfaces.nsIClipboard);
    if (!clip) return false;
    
    var trans = Components.classes["@mozilla.org/widget/transferable;1"].createInstance(Components.interfaces.nsITransferable);
    if (!trans) return false;
    trans.addDataFlavor("text/unicode");

    clip.getData(trans, clip.kGlobalClipboard);

    var str       = new Object();
    var strLength = new Object();

    trans.getTransferData("text/unicode", str, strLength);

    if (str) str = str.value.QueryInterface(Components.interfaces.nsISupportsString);
    if (str) pastetext = str.data.substring(0, strLength.value / 2);
    return pastetext;
  },

 copy: function(txt){
    //fixme: http://developer.mozilla.org/en/docs/Using_the_Clipboard
    var copytext = txt;

    var str   = Components.classes["@mozilla.org/supports-string;1"].
    createInstance(Components.interfaces.nsISupportsString);
    if (!str) return false;

    str.data  = copytext;
    
    var trans = Components.classes["@mozilla.org/widget/transferable;1"].
    createInstance(Components.interfaces.nsITransferable);
    if (!trans) return false;
    
    trans.addDataFlavor("text/unicode");
    trans.setTransferData("text/unicode", str, copytext.length * 2);
    
    var clipid = Components.interfaces.nsIClipboard;
    var clip   = Components.classes["@mozilla.org/widget/clipboard;1"].getService(clipid);
    if (!clip) return false;
    
    clip.setData(trans, null, clipid.kGlobalClipboard);
    return true;
  }
 
};
