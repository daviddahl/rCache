function Querystring(qs) { // optionally pass a querystring to parse
  this.params = new Object();
  this.get=Querystring_get;
    
    if (qs == null)
      qs=location.search.substring(1,location.search.length);
	
    if (qs.length == 0)
      return
			      
// Turn <plus> back to <space>
// See: http://www.w3.org/TR/REC-html40/interact/forms.html#h-17.13.4.1
	qs = qs.replace(/\+/g, ' ')
	var args = qs.split('&') // parse out name/value pairs separated via &
	
// split out each name=value pair
	for (var i=0;i<args.length;i++) {
		var value;
		var pair = args[i].split('=');
		var name = unescape(pair[0]);

		if (pair.length == 2)
		  value = unescape(pair[1]);
	        else
		  value = name;
		
		this.params[name] = value;
	}
}

function Querystring_get(key, default_) {
	// This silly looking line changes UNDEFINED to NULL
	if (default_ == null) default_ = null;
	
	var value=this.params[key]
	if (value==null) value=default_;
	
	return value
}

/////////////////////////////////////
//Start rcache_it ///////////////////
/////////////////////////////////////

function rcache_it(){
  window.setTimeout("spider.getURI()",2000);
}

var spider = {

 init: function(){
    cache_results = document.getElementById('caching_status');
  },

 getURI: function(){
    var qs = new Querystring();
    var url = '/spider/?url=' + qs.get("url");
    //alert(url);
    var cObj = YAHOO.util.Connect.asyncRequest('GET', url, spiderCallBk);
    //alert(cObj);
  },
 
};

var spiderCallBk = {

 success: function(o){
    var spider_results = eval('(' + o.responseText + ')');
    //display results inside caching_status div
    res_div = document.getElementById('caching_status');
    res_div.innerHTML = "";
    //wrapper div for results
    results_data = document.createElement('div');
    results_data.className = "spider_results";
    //first section: title:
    title = document.createElement('div');
    title.className = "results_section";
    title.innerHTML = spider_results.title;
    
    var form_wrap = createDOM('div');
    form_wrap.className = "results_section";

    var tag_form = createDOM('form' ,{'action':'javascript:spiderTags()'});
    var tag_input = createDOM('input',{'type':'text',
	  'name':'tags',
	  'maxlength':100,
	  'size':40,
	  'title':'Enter all tags here: "Politics,Criminals,etc..."'}
      );
    var tag_entry_id = createDOM('input',{'type':'hidden',
	  'name':'entry_id',
	  'value':spider_results.id,
	  'id':'entry_id'}
      );
    var form_button = createDOM('input',{'type':'submit',
	  'value':'save tags','title':'Separate tags with a comma ","'});
    tag_form.appendChild(tag_input);
    tag_form.appendChild(form_button);
    form_wrap.appendChild(tag_form);

    var body = document.createElement('div');
    body.innerHTML = '<pre>' + spider_results.txt + '</pre>';
    
    results_data.appendChild(form_wrap);
    results_data.appendChild(title);
    results_data.appendChild(body);
    res_div.appendChild(results_data);
    
  },

 failure: function(o){
    alert('Your rCache request is being processed, please check your entries list in a few minutes');
  },
 timeout: 15000
}

/////////////////////////////////////
//Start spiderTags ///////////////////
/////////////////////////////////////

function spiderTags(){
  window.setTimeout("tags.submit()",2000);
}

var tags = {

 postTags: function(){
    var tags = document.getElementById('tags_input').value;
    var entry_id = document.getElementById('entry_id').value;
    var url = '/spider_tags/?tags=' + tags + '&id=' + entry_id;
    //alert(url);
    var cObj = YAHOO.util.Connect.asyncRequest('POST', url, spiderTagsCallBk);
    //alert(cObj);
  },
 
};

var spiderTagsCallBk = {

 success: function(o){
    var results = eval('(' + o.responseText + ')');
    //display results inside caching_status div
    var res_div = document.getElementById('caching_status');
    res_div.innerHTML = "";
    //wrapper div for results
    var results_data = document.createElement('div');
    results_data.className = "spider_results";
    //first section: title:
    var title = document.createElement('div');
    title.className = "results_section";
    title.innerHTML = spider_results.title;
    
    var form_wrap = createDOM('div');
    form_wrap.className = "results_section";

    var tag_form = createDOM('form' ,{'action':'javascript:spiderTags.submit()'});
    var tag_entry_id = createDOM('input',{'type':'hidden',
	  'name':'entry_id',
	  'value':results,
	  'id':'entry_id'});
    var tag_input = createDOM('input',{'type':'text',
	  'name':'tags',
	  'maxlength':100,
	  'size':40,
	  'id':'tags_input',
	  'title':'Enter all tags here: "Politics,Criminals,etc..."'});
    var form_button = createDOM('input',{'type':'submit',
	  'value':'save tags','title':'Separate tags with a comma ","'});
    tag_form.appendChild(tag_input);
    tag_form.appendChild(form_button);
    form_wrap.appendChild(tag_form);

    var body = document.createElement('div');
    body.innerHTML = '<pre>' + spider_results.txt + '</pre>';
    
    results_data.appendChild(form_wrap);
    results_data.appendChild(title);
    results_data.appendChild(body);
    res_div.appendChild(results_data);
    
  },

 failure: function(o){
    alert('Your rCache request is being processed, please check your entries list in a few minutes');
  },
 timeout: 10000
}









//////////////////////////////////////////////////
//JSSpider////////////////////////////////////////
//////////////////////////////////////////////////
var jsSpider = {

 init: function(){
    cache_results = document.getElementById('caching_status');
  },

 getURI: function(){
    var qs = new Querystring();
    var url = qs.get("url");
    //alert(url);
    try {
      netscape.security.PrivilegeManager.enablePrivilege("UniversalPreferencesRead")
	//netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");
      var cObj = YAHOO.util.Connect.asyncRequest('GET', url, JsSpiderCallBk);
      //alert(cObj);
    } catch (e) {
      alert("Permission UniversalBrowserRead denied.");
    }
    
  },
 
 displayDetails: function(){
    //alert("displaying details");
  }


};

var JsSpiderCallBk = {

 success: function(o){
    var spider_results = eval('(' + o.responseText + ')');
    //display results inside caching_status div
    res_div = document.getElementById('caching_status');
    res_div.innerHTML = "";
    //wrapper div for results
    results_data = document.createElement('div');
    results_data.className = "spider_results";
    //first section: title:
    // title = document.createElement('div');
//     title.className = "results_section";
//     title.innerHTML = spider_results.title;
    
    body = document.createElement('div');
    body.innerHTML = '<pre>' + spider_results + '</pre>';

    //results_data.appendChild(title);
    results_data.appendChild(body);
    res_div.appendChild(results_data);
    
    
    
  },

 failure: function(o){
    alert('Your rCache request is being processed, please check your entries list in a few minutes');
  },
 timeout: 10000
}
