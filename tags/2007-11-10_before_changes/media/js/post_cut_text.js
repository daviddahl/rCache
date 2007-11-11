function getSel(){
  var txt = '';
  var foundIn = '';
  if (window.getSelection){
    txt = window.getSelection();
    foundIn = 'window.getSelection()';
  }
  else if (document.getSelection)
    {
      txt = document.getSelection();
      foundIn = 'document.getSelection()';
    }
  else if (document.selection)
    {
      txt = document.selection.createRange().text;
      foundIn = 'document.selection.createRange()';
    }
  return txt;
}
var post_rcache = function(txt,url){
  txt = encode(txt);
  url = encode(url);
  var url_post = 'https://127.0.0.1:8000/?text=' + txt + '&url=' + url;
  //alert(url);
  var cObj = YAHOO.util.Connect.asyncRequest('POST', url_post, alert_callbk);
    //alert(cObj);
};
var alert_callbk = function(o){  
 success: function(){
    alert("hmmm");
  }
 failure: function(o){
    alert("failure");
  }
 timeout: 10000;
};
url = location.href;
txt = getSel();
post_rcache(txt,url);
