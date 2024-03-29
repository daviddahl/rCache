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


String.prototype.trim = function () {
    return this.replace(/^\s+|\s+$/g, "");
}; 

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

//start new rCache object

var rcache = new Object();
var xhr = new Object();
var entry = new Object();

rcache.entry = entry;

rcache.xhr = xhr;


rcache.entry.new_entry_submit = function(){
    // disable the submit button then submit the form
    //var loading = $('<img src="/media/img/indeterminate-progress-bar.gif"/>');
    $("#progress-bar").show();
    //$("#progress-bar").append(loading);
    $("#submit").hide();
    //$("#uploader")[0].submit();
    return true;
}

rcache.xhr.related_add_kword = function(kword){
    // add a keyword to the kwords span
    var existing_kwords = $('#related-doc-keywords')[0].innerHTML;
    //alert(existing_kwords);
    if (existing_kwords == ''){
	$('#related-doc-keywords')[0].innerHTML = existing_kwords + kword + " ";
    } else {
	var e_kwords_arr = existing_kwords.split(" ");
	if (e_kwords_arr.indexOf(kword) >= 0){
	    //already in array
	} else {
	    $('#related-doc-keywords')[0].innerHTML = existing_kwords + kword + " ";
	}
    }
}
rcache.xhr.related_docs_custom_kwords_clear = function(){
    $('#related-doc-keywords')[0].innerHTML = '';
}

rcache.xhr.related_docs_custom_kwords = function(){
    // get the keywords from the span holding them, pass them to 'related_docs'
    var kwords_str = $('#related-doc-keywords')[0].innerHTML;
    kwords_str.trim()
    if (kwords_str == ''){
	alert("Please select one or more keywords.");
    } else {
	var kwords_arr = kwords_str.split(" ");
	var kwords = kwords_arr.join(" AND ");
	
	$("#related-docs")[0].innerHTML = '<img src="/media/img/indeterminate-progress-bar.gif" border="0"/>';
	$("#related-docs").css({'border':'1px solid #eee','padding':'4px'});
	rcache.xhr.related_docs(kwords);
    }
}

rcache.xhr.related_docs = function(kwords){
    // fixme: use AND between all keywords!!!!!!!!!!
    // get related docs via a docs' keywords
    var query = kwords;
    //var kwords_arr = kwords.split(' ',3);
    //query = query + kwords_arr.join(' ');
    var post_data = {'search_str':query};
    var url = "/xhr/search/";
    $.post(url,post_data,function(data,textStatus){
	    res = eval('(' + data  + ')');
	    if (res.status == 'success'){
		$("#related-docs").children().remove();
		$("#related-docs")[0].innerHTML = res.msg;
		$("#related-docs").css({'border':'1px solid #eee',
			    'padding':'4px',
			    'max-height':'200px',
			    'overflow':'auto'});
		$("#related-docs > table").css({'width':'100%'});
		$("#related-docs").show("slow");
	    } else {
		alert(res.msg);
	    }
	});
}

rcache.xhr.clear_input = function(inpt){
    // clear search input
    inpt.value = "";
    inpt.onclick = null;
}

rcache.xhr.search = function(){
    // perform a search - use base64 encoding on search query
    var qs = encodeURIComponent($('#search-inpt')[0].value);
    // get input value
    // base64 encode it
    // change location to /search/?q=jhfjdhfldhgfkdhfdjh
    if (qs){
	document.location = "/search/?search_str=" + qs;
    } else {
	alert("Please enter a search term.");
    }
    
}

rcache.xhr.entries_with_link = function(link_id){
    var url = "/xhr/entries/with/link/" + link_id + "/";
    $.get(url,function(data){
	    var res = eval('(' + data + ')');
	    if (res.status == 'success'){
		var entries = $(res.entries);
		//alert(res.entries);
		$("#link-entries-" + res.link_id).children().remove();
		$("#link-entries-" + res.link_id).append(entries);
	    } else {
		//fixme: install jqModal
		alert("No other entries contain this link");
	    }
	});
}

function showKeyCode(e)
{
    //alert("keyCode for the key pressed: " + e.keyCode + "\n");
}

function checkSubmission(e){
    // check for return "13"
    // alert(e.keyCode);
    if (e.which == 13){
	rcache.xhr.search();
	return true;
    } else {
	return false;
    }   
}

save_link = function(){
    var url = encodeURIComponent(document.location);
    var title = '';
    var description = '';
    var keywords = '';
    try{
	var head = document.getElementsByTagName('head')[0].childNodes;
	for(i=0; i<=head.length; i++){
	    try{
		//fixme: evaluate all of the head elements as lowercase
		if (head[i].getAttribute('name').toLowerCase()=='description'){
		    description = encodeURIComponent(
				  head[i].getAttribute('content'));
		}
		if (head[i].getAttribute('name').toLowerCase()=='keywords'){
		    keywords = encodeURIComponent(
                               head[i].getAttribute('content'));
		}
	    }catch(e){
		//do nothing
	    }
	}
    } catch(e){
	var head = null;
    }
    try{
	title = encodeURIComponent(document.getElementsByTagName('title')[0].innerHTML);
    }catch(e){
	title = encodeURIComponent('No title');
    }

    var save_link_url  = 'http://127.0.0.1:8000/save/link/?url=' + 
        url + '&title=' + title + '&description=' + description +
        '&keywords=' + keywords;
    document.location = save_link_url;
    /*return {'url':url,
	    'title':title,
	    'description':description,
	    'keywords':keywords,
	    'save_lnk':save_link_url};
    */
};


var viz = new Object();

rcache.viz = viz;

rcache.viz.setup = function(){
    $(".viz-tag-box > a").hide();
};

rcache.viz.mouse_ovr = function(el){
    // do some animation when mouse over occurs
    try {
	$(".viz-expanded").animate({'padding':'4px','font-size':''});
	$(".viz-expanded").css({'font-size':'','float':'left','background':''});
	$(".viz-tag-box").removeClass('viz-expanded');
	
    } catch(e){
	// do nothing
    }

    $(el).animate({'padding':'4px','font-size':'12px'});
    $(el).css({'font-size':'12px','float':'','background':''});
    $(el).addClass('viz-expanded');
};

rcache.viz.mouse_out = function(el){
    // do some animation when mouse over occurs
    $(el).animate({'padding':'4px','font-size':''});
    $(el).css({'font-size':'','float':'left','background':''});
};

rcache.viz.recent_tagged_with = function(id){
    // get recently tagged entry titles
    var the_div = $("#viz-detail-box");
    var url ='/viz/xhr/recent/tagged/with/' + id +"/";
    $.get(url,function(data){
	    var res = eval('(' + data + ')');
	    if (res.status == 'success'){
		var entries = $(res.msg);
		//alert(res.msg);
		try{
		    $("._entries").children().remove();
		    $("._entries").removeClass('_entries');
		}catch(e){
		    // blah!
		    //alert(e);
		}
		//the_div.children().remove();
		the_div.append(entries);
		the_div.addClass("_entries");
	    } else {
		//fixme: install jqModal
		alert("could not get entries for tag");
	    }
	});
};

function UnCryptMailto(s) {
    var n=0;
    var r="";
    for(var i=0; i < s.length; i++) {
	n=s.charCodeAt(i);
	if (n>=8364) {n = 128;}
	r += String.fromCharCode(n-(1));
    }
    return r;
}




$(document).ready(function(){
	$(".rounded-top").corner("top round 6px");
	$(".rounded").corner("8px");
	$("ul.nav-edit li").corner("tr br round 6px");

});
