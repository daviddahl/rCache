//utilities for DOM extraction, etc...

//string = document.referrer 

var fragmentMiner = {
 
 makeFrag: function(selection){
    var rng = selection.getRangeAt(0);
    var clone = rng.cloneContents();
    return clone;
  },

 getAnchors: function(fragment){
    //pass a fragment and tag to traverse to return an array of wanted tag data
    if (fragment.hasChildNodes() == true){
      var y = fragment.childNodes;
      var result = [];
      for (i=0;i<y.length;i++){
	if (y[i].nodeType!=3){
	  if (y[i].nodeName == 'A'){
	    result.push(y[i].href);
	  }
	  for (z=0;z<y[i].childNodes.length;z++){
	    if (y[i].childNodes[z].nodeType!=3){
	      if (y[i].childNodes[z].nodeName == 'A'){
		result.push(y[i].childNodes[z].href);
	      }
	    }
	  }
	}
      }
      //fixme: need to make all href's absolute
      return result;
    }
  }, 
    
 getImgSrc: function(fragment){
    //pass a fragment to traverse to return an array of wanted tag data
    if (fragment.hasChildNodes() == true){
      var y = fragment.childNodes;
      var result = [];
      for (i=0;i<y.length;i++){
	if (y[i].nodeType!=3){
	  if (y[i].nodeName == 'IMG'){
	    result.push(y[i].src);
	  }
	  for (z=0;z<y[i].childNodes.length;z++){
	    if (y[i].childNodes[z].nodeType!=3){
	      if (y[i].childNodes[z].nodeName == 'IMG'){
		result.push(y[i].childNodes[z].src);
	      }
	    }
	  }
	}
      }
      //fixme: need to make all src's absolute
      return result;
    }
  }

};
