//testing stuff

var sel = window.getSelection();

sel.rangeCount;

var rng = sel.getRangeAt(0);

var ext = rng.extractContents();
var ext = rng.cloneContents();


ext.hasChildNodes();

ext.nodeType;
//returns 11 (document fragment node)

var chld = ext.firstChild;

chld.nodeName; //returns HTML TAG or '#document-fragment' is obj is doc frag
ext.nextSibling;


function countTags(n) {                         // n is a Node 
    var numtags = 0;                            // Initialize the tag counter
    if (n.nodeType == 1 /*Node.ELEMENT_NODE*/)  // Check if n is an Element
        numtags++;                              // Increment the counter if so
    var children = n.childNodes;                // Now get all children of n
    for(var i=0; i < children.length; i++) {    // Loop through the children
        numtags += countTags(children[i]);      // Recurse on each one
    }
    return numtags;                             // Return the total number of tags
}
