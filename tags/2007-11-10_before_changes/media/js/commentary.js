var commentary = {

 snippet_show: function(id){
    var url = "/commentary/snippet_xhr/" + id +"/";
    commentary.current_snip_id = id;
    var snip_div_id = 'snippet_' + commentary.current_snip_id;
    var snip_div = document.getElementById(snip_div_id);
    snip_div.className = 'snippet';
    this.snippetShowConn(url);
  },

 snippet_hide: function(id){
    var url = "/commentary/snippet_hide_xhr/" + id +"/";
    commentary.current_snip_id = id;
    var snip_div_id = 'snippet_' + commentary.current_snip_id;
    //alert(snip_div_id);
    var snip_div = document.getElementById(snip_div_id);
    snip_div.className = 'snippet-hidden';
    snip_div.innerHTML = '';
    snip_div.innerHTML = '<a href="#" onclick="javascript:commentary.snippet_show(' + id +');" class="button-small" title="Show Hidden Snippet">+</a>';
    this.snippetHideConn(url);
  },

 snippetShowConn: function(url){
    var cObj = YAHOO.util.Connect.asyncRequest('GET', url, 
					       commentary.snippetShowCallBk);
  },
 
 snippetHideConn: function(url){
    var cObj = YAHOO.util.Connect.asyncRequest('GET', url, 
					       commentary.snippetHideCallBk);
  },

 current_snip_id: null,

 snippetShowCallBk: {

  success: function(o){
      var res = eval('(' + o.responseText + ')');
      //re-create snippet and all comments
      var snip_div_id = 'snippet_' + commentary.current_snip_id;
      //alert(snip_div_id);
      var snip_div = document.getElementById(snip_div_id);
      snip_div.innerHTML = '';
      var txt_frmtr = document.createElement('pre');
      txt_frmtr.innerHTML = res.snippet.snippet;
      snip_div.appendChild(txt_frmtr);
      var snip_opts = document.createElement('div');
      var opt_lnk1 = '<a href="#" class="button-small" title="Hide Snippet" onclick="javascript:commentary.snippet_hide(' + commentary.current_snip_id + ');">-</a> ';
      //var opt_lnk2 = '<a href="#" class="button-small" title="Remove Snippet" onclick="commentary.snippet_remove(' + commentary.current_snip_id + ');">X</a> ';
      var opt_lnk3 = '<a href="#" class="button-small" onclick="commentary.comment_new(snippet=' + commentary.current_snip_id + ');">New Comment</a> ';
      snip_opts.innerHTML = opt_lnk1 + opt_lnk3;
      var comments = document.createElement('div');
      comments.className = 'comments';
      snip_div.appendChild(snip_opts);
      snip_div.appendChild(comments);
      return false;
    },

  failure: function(o){
      alert('Connection Problem, please try again in a moment.');
    },

  timeout: 5000

  },

 snippetHideCallBk: {

  success: function(o){
      //set the snippet to inactive!
      var res = eval('(' + o.responseText + ')');
      return false;
    },
  
  failure: function(o){
      alert('Connection Problem, please try again in a moment.');
    },
  
  timeout: 5000

 },

 comment_new: function(id){
    //create text input and save button
    //display in new-comment div
    txtarea_id = "new_comment_" + id;
    if (document.getElementById(txtarea_id) == null){
      var div_id = "new_comment_snippet_" + id;
      comment_div = document.getElementById(div_id);
      comment_div.className = 'new-comment';
      var txtarea = document.createElement('textarea');
      txtarea.id = "new_comment_" + id;
      txtarea.className = 'new-comment-txt';
      var sub_button = document.createElement('a');
      sub_button = '&nbsp;&nbsp;<a href="#" onclick="javascript:commentary.comment_post(' + id + ',0);" class="button-small" style="margin-bottom:0.6em;">Post</a> &nbsp;&nbsp;<a href="#" onclick="javascript:commentary.comment_cancel(' + id + ');" class="button-small" style="margin-bottom:0.6em;">Cancel</a>';
      var form_lst = document.createElement('ul');
      form_lst.className = 'comment-form-lst';
      var li1 = document.createElement('li');
      li1.appendChild(txtarea);
      var li2 = document.createElement('li');
      li2.innerHTML = sub_button;
      form_lst.appendChild(li1);
      form_lst.appendChild(li2);
      comment_div.appendChild(form_lst);
    } else {
      alert('The new comment textarea exists');
    }
    
  },

 comment_post: function(id,parent){
    //get textarea comment
    var comm_id = 'new_comment_' + id;
    var comment = document.getElementById(comm_id);
    //alert(comment.value);
    //need to encode the text
    var the_comment = encodeURIComponent(comment.value);
    if (the_comment != ''){
      var post_data = "snippet=" + id + "&comment=" + the_comment + "&parent=" + parent;
      var url = "/commentary/comment_new_xhr/";

      this.comment_new_xhr(url,post_data);
    }
  },

 comment_new_xhr: function(url,post_data){
    var cObj = YAHOO.util.Connect.asyncRequest('POST',
					       url, 
					       commentary.CommNewCallBk, 
					       post_data);
  },
 
 CommNewCallBk: {

  success: function(o){
      var res = eval('(' + o.responseText + ')');
      if (res.result == 'Success'){ 
	//need to wipe form out and re-display as a comment
	var comm_div_id = 'new_comment_snippet_' + res.snippet_id;
	var comm_div = document.getElementById(comm_div_id);
	comm_div.innerHTML = '';
	var newcomm_div = document.createElement('div');
	var newcomm_pre = document.createElement('pre');
	newcomm_pre.innerHTML = res.comment;
	newcomm_div.appendChild(newcomm_pre);
	newcomm_div.className = 'comment';
	comm_div.appendChild(newcomm_div);
	return false;
      } else {
	alert(res.message);
      }
    },

  failure: function(o){
      alert('Error: Could not post comment, please try again in a few seconds.');
    },

  timeout: 5000

 },

 comment_cancel: function(id){
    //remove new comment div
    var div_id = "new_comment_snippet_" + id;
    comment_div = document.getElementById(div_id);
    comment_div.innerHTML = '';
    return;
  }

};
