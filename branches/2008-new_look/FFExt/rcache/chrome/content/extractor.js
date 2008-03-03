var extractor = new Object();

extractor.browser_window = null;
extractor.window_title = null;
extractor.extractor_window = null;
extractor.fragment_element = null;
extractor.selected_txt = null;

extractor.media = new Object();
extractor.links = new Array();
extractor.images = new Array();
extractor.rgx = new Object();

extractor.upload_queue = new Object();
extractor.downloaded_media = new Object();

extractor.url = function(){
    return 'http://127.0.0.1:8000/extract/';
};

extractor.login_url =  function(){
    return "http://127.0.0.1:8000/loginxul/";
};

extractor.window_url = function(){
    // get current url
    this.window_location = getBrowser().currentURI.spec;
    return this.window_location;
};

extractor.the_title = function(){
    this.window_title = this.browser_window.document.title;
    return this.window_title;
};

extractor.log = function(msg){
    try{
	console.log(msg);
    } catch(e){
	alert('debugging is on... no logging console found:(');
	alert(msg);
    }
};


extractor.initialize_regexes = function(){
    // handy regexes!
    
    this.rgx.img = /.jpg$|.png$|.jpeg$|.gif$/i;
    this.rgx.media = /.doc$|.xls$|.ppt$|.pdf$|.rtf$|.txt$/i;
    this.rgx.doc = /.doc$/i;
    this.rgx.xls = /.xls$/i;
    this.rgx.ppt = /.ppt$/i;
    this.rgx.pdf = /.pdf$/i;
    this.rgx.rtf = /.rtf$/i;
    this.rgx.txt = /.txt$/i;
    this.rgx.jpg = /.jpg$|.jpeg$/i;
    this.rgx.png = /.png$/i;
    this.rgx.gif = /.gif$/i;

    this.rgx_mtrx = [[this.rgx.img,'img'],
		     [this.rgx.media,'media'],
		     [this.rgx.doc,'doc'],
		     [this.rgx.xls,'xls'],
		     [this.rgx.ppt,'ppt'],
		     [this.rgx.pdf,'pdf'],
		     [this.rgx.rtf,'rtf'],
		     [this.rgx.txt,'txt'],
		     [this.rgx.jpg,'jpg'],
		     [this.rgx.png,'png'],
		     [this.rgx.gif,'gif']
		     ];

};

extractor.browser_window = null;    

extractor.extractor_win = function(){
    var ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(Components.interfaces.nsIWindowWatcher);
    var win = ww.openWindow(null,
			    "chrome://rcache/content/rcache_collector.xul", 
    			    "status", 
    			    "chrome,resizable", null);
    this.extractor_window = win;
    return win;
    
};

extractor.start = function(){
    //entry point for the new extractor:
    // 1. get selection
    // 2. parse links
    // 3. parse images
    // 4. parse documents: PDF, Word, PPT, XLS, rtf, txt, etc...
    // 5. parse embeded objects
    // 6. postcache main selected content/links/imagelinks
    // 7. postcache additional selected media
    
    this.initialize_regexes();
    var sel = this.selection();
    this.window_url();
    this.the_title();

    if (sel == false){
	return;
    } else {
	var frag = this.fragment();
	this.links = jQuery(this.fragment_element).find('a');
	//alert(this.links.length);
	this.organize_media();
	//alert(this.media['doc']);
	this.images = jQuery(this.fragment_element).find('img');
	//test jQuery
	//this.main_window_test();
	//launch rcache extractor XUL window
	this.extractor_win();
	this.load_extractor_window();
    }
};

extractor.selection = function(){
    var wndw=document.commandDispatcher.focusedWindow;
    this.browser_window = wndw;
    var selected_txt=wndw.getSelection();
    if (selected_txt == ''){
	alert("rCache Error: Please select a portion of this page.");
	return false;
    }
    this.selected_txt = selected_txt;
    return selected_txt;
};

extractor.fragment = function(){
    try{
	var txt = this.selected_txt;
	var rng = txt.getRangeAt(0);
	var frag = rng.cloneContents();
	var element = content.document.createElement("DIV");    
	element.id = "rcache-tmp";
	element.appendChild(frag);
	this.fragment_element = element;
	return element;
	
    } catch(e){
	alert(e);
    }
};

extractor.parse_links = function(regex){
    // organize all media into this.media
    var arr = new Array();
    for(var i=0; i < this.links.length; i++){
	if (regex[0].test(this.links[i].href)){
	    if (arr.indexOf(this.links[i]) == -1){
		arr.push(this.links[i]);
	    }
	}
    }
    var key = regex[1];
    this.media[key] = arr;

};

extractor.organize_media = function(){
    for(var i=0; i < this.rgx_mtrx.length; i++){
	this.parse_links(this.rgx_mtrx[i]);
    }
};


extractor.load_extractor_window = function(){
    // load the window with media, links, text, title, metadata
    // add text to the text area:
    var confirmwin = this.extractor_window;
    var txt = this.selected_txt;
    var title = this.the_title();
    var url = this.window_url();
    var links = this.links;
    var media = this.media;
    var imgs = this.images;
    var media = this.media;

    var loadFunction = function() {
	var selTex = confirmwin.document.getElementById('selectedtext');
	selTex.setAttribute("value",txt);
	var pgTitle = confirmwin.document.getElementById('pagetitle');
	pgTitle.setAttribute("value",title);
	var pgUrl = confirmwin.document.getElementById('url');
	pgUrl.setAttribute("value",url);

	// add links to link listbox
	var linksLst = confirmwin.document.getElementById('linkbox');   
	for (var i = 0; i < links.length; i++){
	    linksLst.appendItem(links[i]);	
	}
	// add images to image listbox
	var imgLst = confirmwin.document.getElementById('imgbox');
	for (var i = 0; i < imgs.length; i++){
	    imgLst.appendItem(imgs[i]);	
	}
	// add all media to the media listbox
	var mediaLst = confirmwin.document.getElementById('media-lst');
	for (var i = 0; i < media['media'].length; i++){
	    mediaLst.appendItem(media['media'][i].href);	
	}
	
    };
    this.extractor_window.addEventListener("load", loadFunction, false); 
};

extractor.main_window_test = function(){
    // try to get a dom obj in xul from jquery
    try{
	var main_window = jQuery('#main-window');
	alert(main_window);
    } catch(e){

    }
};

extractor.download_media = function(){
    // download a media object, store in this.downloaded_media() like so:
    // downloaded_media['url'] = {'url':url,'mime_type':mime_type,'size':size'}
    var lstbx = document.getElementById('media-lst');
    var url = lstbx.getSelectedItem(0);
    var progress = document.getElementById('media-dl-progress');
    progress.value = 0;
    try{
	var data = this.download(url.label);
	var dl_obj = {'data':data,'url':url.label,'mime_type':mime_type};
	this.downloaded_media.push(dl_obj);
	var dl_obj = null;
    } catch(e){
	alert(e);
    }
    
};

extractor.download = function(){
    // do the download!
    var lstbx = document.getElementById('media-lst');
    var url = lstbx.getSelectedItem(0).label;
    var dl_desc = document.getElementById('media-dl-desc');
    dl_desc.setAttribute("value","Downloading: " + url );
    var before = function(){
	this.onprogress = extractor.on_progress;
    };
    var completed = function(){
	alert('Download Complete');
    }; 
    var o = {'url':url,type:'GET',beforeSend:before,dataType:'text',complete:completed};
    var http = jQuery.ajax(o);
    
};

extractor.status_msg =  function(){
    window.document.getElementById('statusmsg').value = "Sucessful rCache.";
}

extractor.on_progress = function(e){
    try{
	var progress = document.getElementById('media-dl-progress');
	var percentComplete = (e.position / e.totalSize)*100;
	progress.value = percentComplete;
    } catch(e) {
	alert(e);
    }
};          
