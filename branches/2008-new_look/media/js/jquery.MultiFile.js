/*
 ### jQuery Multiple File Upload Plugin v1.24 - 2008-01-14 ###
 By Diego A., http://www.fyneworks.com, diego@fyneworks.com
 
 Website:
  http://www.fyneworks.com/jquery/multiple-file-upload/
 Project Page:
  http://jquery.com/plugins/project/MultiFile/
 Forums:
  http://www.nabble.com/jQuery-Multiple-File-Upload-f20931.html
 Blog:
  http://fyneworks.blogspot.com/2007/04/jquery-multiple-file-upload-plugin-v11.html
  (old) http://fyneworks.blogspot.com/2007/04/multiple-file-upload-plugin-for-jquery.html
 
 12-April-2007: v1.1
                Added events and file extension validation
                See website for details.
 
 06-June-2007: v1.2
                Now works in Opera.
 
 12-June-2007: v1.21
                Preserves name of file input so all current server-side
                functions don't need to be changed on new installations.
 
 24-June-2007: v1.22
                Now works perfectly in Opera, thanks to Adrian Wróbel <adrian [dot] wrobel [at] gmail.com>
 
 10-Jan-2008: v1.24
                Fixed bug in event trigger - sending incorrect parameters to event handlers
 
 14-Jan-2008: v1.24
                Fixed bug 1251: http://plugins.jquery.com/project/comments/add/1251
*/

/*# AVOID COLLISIONS #*/
if(jQuery) (function($){
/*# AVOID COLLISIONS #*/

 // Fix for Opera: 6-June-2007
 // Stop confusion between null, 'null' and 'undefined'
 function IsNull(i){
  return (i==null || i=='null' || i=='' || i=='undefined');
 };
 
 // extend jQuery - $.MultiFile hook
 $.extend($, {
  MultiFile: function( o /* Object */ ){
   return $("INPUT[@type='file'].multi").MultiFile(o);
  }
 });
 
 // extend jQuery function library
 $.extend($.fn, {
   
   // MultiFile function
   MultiFile: function( o /* Object */ ){
    if(this._MultiFile) return $(this);
    this._MultiFile = true;
    
    // DEBUGGING: disable plugin
    //return false;
    
    // Bind to each element in current jQuery object
    return $(this).each(function(i){
       // BUG 1251 FIX: http://plugins.jquery.com/project/comments/add/1251
       // variable i would repeat itself on multiple calls to the plugin.
       // this would cause a conflict with multiple elements
       // changes scope of variable to global so id will be unique over n calls
       window.MultiFile = (window.MultiFile || 0) + 1;
       i = window.MultiFile;
       
       // Remember our ancestors...
       var MASTER = this;
       
       // Copy parent attributes - Thanks to Jonas Wagner
       // we will use this one to create new input elements
       var xCLONE = $(MASTER).clone();
       
       //#########################################
       // Find basic configuration in class string
       // debug???
       MASTER.debug = (MASTER.className.indexOf('debug')>0);
       // limit number of files that can be selected?
       if(IsNull(MASTER.max)){
        MASTER.max = $(MASTER).attr('maxlength');
        if(IsNull(MASTER.max)){
         MASTER.max = ((MASTER.className.match(/\b((max|limit)\-[0-9]+)\b/gi) || [''])[0]);
         if(IsNull(MASTER.max)){
          MASTER.max = -1;
         }else{
          MASTER.max = MASTER.max.match(/[0-9]+/gi)[0];
         }
        }
       };
       MASTER.max = new Number(MASTER.max);
       // limit extensions?
       if(!MASTER.accept){
        MASTER.accept = (MASTER.className.match(/\b(accept\-[\w\|]+)\b/gi)) || '';
        MASTER.accept = new String(MASTER.accept).replace(/^(accept|ext)\-/i,'');
       };
       //#########################################
       
       // DEBUGGING: report status in Firebug console
       /*DBG*/// MASTER.debug = true;
       /*DBG*/// if(MASTER.debug && console) console.log('MultipleFile Upload plugin debugging enabled on "'+(MASTER.id?'#':'')+''+(MASTER.id || MASTER.name)+'"');
       
       // Attach a bunch of events, jQuery style ;-)
       /*DBG*/// $.each("on,after".split(","), function(i,o){
       /*DBG*///  $.each("FileSelect,FileRemove,FileAppend".split(","), function(j,event){
       /*DBG*///   MASTER[o+event] = function(element, value, master){ // default event handlers just show debugging info...
       /*DBG*///    if(MASTER.debug && console) console.log('*** '+o+event+' *** DEFAULT HANDLER' +'\nElement:' +element.name+ '\nValue: ' +value+ '\nMaster: ' +master.name+ '');
       /*DBG*///   };
       /*DBG*///  });
       /*DBG*/// });
       
       // Setup a global event handler
       MASTER.trigger = function(event, element){
        var handler = MASTER[event];
        var value = $(element).attr('value');
        /*DBG*/// if(MASTER.debug && console) console.log('*** TRIGGER EVENT: '+event+' ***' +'\nCustom Handler:' +(handler ? 'Yes':'No') +'\nElement:' +element.name+ '\nValue: ' +value+ '\nMaster: ' +MASTER.name+ '');
        if(handler){
         var returnValue = handler(element, value, MASTER);
         if( returnValue!=null ) return returnValue;
        }
        return true;
       };
       
       
       // Initialize options
       if( typeof o == 'number' ){ o = {max:o}; };
       $.extend(MASTER, MASTER.data || {}, o);
       
       // Default properties - INTERNAL USE ONLY
       $.extend(MASTER, {
        STRING: MASTER.STRING || {}, // used to hold string constants
        n: 0, // How many elements are currently selected?
        k: 'multi', // Instance Key?
        f: function(z){ return MASTER.k+'_'+String(i)+'_'+String(z); }
       });
       
       // Visible text strings...
       // $file = file name (with path), $ext = file extension
       MASTER.STRING = $.extend({
        remove:'remove',
        denied:'You cannot select a $ext file.\nTry again...',
        selected:'File selected: $file'
       }, MASTER.STRING);
       
       
       // Setup dynamic regular expression for extension validation
       // - thanks to John-Paul Bader: http://smyck.de/2006/08/11/javascript-dynamic-regular-expresions/
       if(String(MASTER.accept).length>1){
        MASTER.rxAccept = new RegExp('\\.('+(MASTER.accept?MASTER.accept:'')+')$','gi');
       };
       
       // Create wrapper to hold our file list
       MASTER.wrapID = MASTER.k+'_'+i; // Wrapper ID?
       $(MASTER).wrap('<div id="'+MASTER.wrapID+'"></div>');
       
       // Bind a new element
       MASTER.add = function( slave, ii ){
        
        // Keep track of how many elements have been displayed
        MASTER.n++;
        
        // Add reference to master element
        slave.MASTER = MASTER;
        
        // Define element's ID and name (upload components need this!)
        slave.i = ii;
        slave.id = MASTER.f(slave.i);
        slave.name = (slave.name || $(MASTER).attr('name') || 'file') + (slave.i>0?slave.i:''); // same name as master element
        
        // If we've reached maximum number, disable input slave
        if( (MASTER.max != -1) && ((MASTER.n-1) > (MASTER.max)) ){ // MASTER.n Starts at 1, so subtract 1 to find true count
         slave.disabled = true;
        };
        
        // Remember most recent slave
        MASTER.current = slave;
        
        /// now let's use jQuery
        slave = $(slave);
        
        // Triggered when a file is selected
        slave.change(function(){
          
          //# Trigger Event! onFileSelect
          if(!MASTER.trigger('onFileSelect', this, MASTER)) return false;
          //# End Event!
          
          // check extension
          if(MASTER.accept){
           var v = String(slave.attr('value'));
           if(!v.match(MASTER.rxAccept)){
            // Clear element value
            slave.val('').attr('value', '');
            slave.get(0).value = '';
            
            // OPERA BUG FIX - 2007-06-24
            // Thanks to Adrian Wróbel <adrian [dot] wrobel [at] gmail.com>
            // we add new input element and remove present one for browsers that can't clear value of input element
            //var f = $('<input name="'+($(MASTER).attr('name') || '')+'" type="file"/>');
            var f = xCLONE.clone();// Copy parent attributes - Thanks to Jonas Wagner
            
            MASTER.n--;
            MASTER.add(f.get(0), this.i);
            slave.parent().prepend(f);
            slave.remove();
            
            // Show error message
            // TO-DO: Some people have suggested alternative methods for displaying this message
            // such as inline HTML, lightbox, etc... maybe integrate with blockUI plugin?
            alert(MASTER.STRING.denied.replace('$ext', String(v.match(/\.\w{1,4}$/gi))));
            
            return false;
           }
          };
          
          // Hide this element: display:none is evil!
          //this.style.display = 'block';
          this.style.position = 'absolute';
          this.style.left = '-1000px';
          
          // Create a new file input element
          //var f = $('<input name="'+($(MASTER).attr('name') || '')+'" type="file"/>');
          var f = xCLONE.clone();// Copy parent attributes - Thanks to Jonas Wagner
          
          // Add it to the form
          $(this).parent().prepend(f);
          
          // Update list
          MASTER.list( this );
          
          // Bind functionality
          MASTER.add( f.get(0), this.i+1 );
          
          //# Trigger Event! afterFileSelect
          if(!MASTER.trigger('afterFileSelect', this, MASTER)) return false;
          //# End Event!
          
        });
       
       };
       // Bind a new element
      
       // Add a new file to the list
       MASTER.list = function( y ){
        
        //# Trigger Event! onFileAppend
        if(!MASTER.trigger('onFileAppend', y, MASTER)) return false;
        //# End Event!
        
        // Insert HTML
        var
         t = $('#'+MASTER.wrapID),
         r = $('<div></div>'),
         v = $(y).attr('value')+'',
         a = $('<span class="file" title="'+MASTER.STRING.selected.replace('$file', v)+'">'+v.match(/[^\/\\]+$/gi)[0]+'</span>'),
         b = $('<a href="#'+MASTER.wrapID+'">'+MASTER.STRING.remove+'</a>');
        t.append(r);
        r.append('[',b,']&nbsp;',a);//.prepend(y.i+': ');
        b.click(function(){
         
          //# Trigger Event! onFileRemove
          if(!MASTER.trigger('onFileRemove', y, MASTER)) return false;
          //# End Event!
          
          MASTER.n--;
          MASTER.current.disabled = false;
          $('#'+MASTER.f(y.i)).remove();
          $(this).parent().remove();
          
          //# Trigger Event! afterFileRemove
          if(!MASTER.trigger('afterFileRemove', y, MASTER)) return false;
          //# End Event!
          
          return false;
        });
        
        //# Trigger Event! afterFileAppend
        if(!MASTER.trigger('afterFileAppend', y, MASTER)) return false;
        //# End Event!
        
       };
       
       // Bind first file element
       if(!MASTER.ft){ MASTER.add(MASTER, 0); MASTER.ft = true; }
       MASTER.I++;
       MASTER.n++;
       
    });
    // each element
   
   }
   // MultiFile function
 
 });
 // extend jQuery function library



/*
 ### Default implementation ###
 The plugin will attach itself to file inputs with the class 'multi' when the page loads.
 Use the jQuery start plugin if available...
*/
if($.start){ $.start($.MultiFile) }
else $(function(){ $.MultiFile() });



/*# AVOID COLLISIONS #*/
})(jQuery);
/*# AVOID COLLISIONS #*/
