/*

DynaCloud v2

A dynamic JavaScript tag/keyword cloud with jQuery.

<http://johannburkard.de/blog/programming/javascript/dynacloud-a-dynamic-javascript-tag-keyword-cloud-with-jquery.html>

MIT license.

Johann Burkard
<http://johannburkard.de>
<mailto:jb@eaio.com>

*/

$(function() {
 jQuery.highlight = document.body.createTextRange ? 

/*
Version for IE using TextRanges .
*/
  function(node, te) {
   var r = document.body.createTextRange();
   r.moveToElementText(node);
   for (var i = 0; r.findText(te); i++) {
    r.pasteHTML('<span class="highlight">' +  r.text + '<\/span>');
    r.collapse(false);
   }
  }

 :

/*
 (Complicated) version for Mozilla and Opera using span tags.
*/
  function(node, te) {
   var pos, skip, spannode, middlebit, endbit, middleclone;
   skip = 0;
   if (node.nodeType == 3) {
    pos=node.data.toUpperCase().indexOf(te);
    if (pos >= 0) {
     spannode = document.createElement('span');
     spannode.className = 'highlight';
     middlebit = node.splitText(pos);
     endbit = middlebit.splitText(te.length);
     middleclone = middlebit.cloneNode(true);
     spannode.appendChild(middleclone);
     middlebit.parentNode.replaceChild(spannode, middlebit);
     skip = 1;
    }
   }
   else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
    for (var i = 0; i < node.childNodes.length; ++i) {
     i += $.highlight(node.childNodes[i], te);
    }
   }
   return skip;
  }

 ;

 $.dynaCloud.stopwords = new RegExp("\\s((" + $.dynaCloud.stopwords.join("|") + ")\\s)+", "gi");
 if ($.dynaCloud.auto) {
  $("*[@class*=dynacloud]").dynaCloud();
 }
});

jQuery.dynaCloud = {

 cloud: {},
 max: 10,
 sort: true,
 auto: true,
 single: true,
 wordStats: true,

// Adapted from <http://www.perseus.tufts.edu/Texts/engstop.html>

 stopwords: [ "a", "about", "above", "accordingly", "after",
  "again", "against", "ah", "all", "also", "although", "always", "am", "an",
  "and", "any", "anymore", "anyone", "are", "as", "at", "away", "be", "been",
  "begin", "beginning", "beginnings", "begins", "begone", "begun", "being",
  "below", "between", "but", "by", "ca", "can", "cannot", "come", "could",
  "did", "do", "doing", "during", "each", "either", "else", "end", "et",
  "etc", "even", "ever", "far", "ff", "following", "for", "from", "further",
  "get", "go", "goes", "going", "got", "had", "has", "have", "he", "her",
  "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into",
  "is", "it", "its", "itself", "last", "lastly", "less", "many", "may", "me",
  "might", "more", "must", "my", "myself", "near", "nearly", "never", "new",
  "next", "no", "not", "now", "o", "of", "off", "often", "oh", "on", "only",
  "or", "other", "otherwise", "our", "ourselves", "out", "over", "perhaps",
  "put", "puts", "quite", "s", "said", "saw", "say", "see", "seen", "shall",
  "she", "should", "since", "so", "some", "such", "t", "than", "that", "the",
  "their", "them", "themselves", "then", "there", "therefore", "these", "they",
  "this", "those", "thou", "though", "throughout", "thus", "to", "too",
  "toward", "unless", "until", "up", "upon", "us", "ve", "very", "was", "we",
  "were", "what", "whatever", "when", "where", "which", "while", "who",
  "whom", "whomever", "whose", "why", "with", "within", "without", "would",
  "yes", "your", "yours", "yourself", "yourselves" ]

};

jQuery.fn.dynaCloud = function() {
 return this.each(function() {
  //var now = new Date().getTime();

  var cl = [];
  var max = 0;

  if (typeof $.wordStats != 'undefined' && $.dynaCloud.wordStats) {
   var count = $.dynaCloud.max == -1 ? 50 : $.dynaCloud.max;
   $.wordStats.computeTopWords(count, this);
   for(var i = 0, j = $.wordStats.topWords.length; i < j && i <= count; ++i) {
    var t = $.wordStats.topWords[i].substring(1);
    if (typeof $.dynaCloud.cloud[t] == 'undefined') {
     $.dynaCloud.cloud[t] = { count: $.wordStats.topWeights[i], el: t };
    }
    else {
     $.dynaCloud.cloud[t].count += $.wordStats.topWeights[i];
    }
    max = Math.max($.dynaCloud.cloud[t].count, max);
   }
   $.wordStats.clear();
  }
  else {
   var elems = $(this).text().replace(/\W/g, " ").replace($.dynaCloud.stopwords, " ").split(" ");
   var word = /^[a-z]*[A-Z]([A-Z]+|[a-z]{3,})/;

   $.each(elems, function(i, n) {
    if (word.test(n)) {
     var t = n.toLowerCase();
     if (typeof $.dynaCloud.cloud[t] == 'undefined') {
      $.dynaCloud.cloud[t] = { count: 1, el: n };
     }
     else {
      $.dynaCloud.cloud[t].count += 1;
     }
     max = Math.max($.dynaCloud.cloud[t].count, max);
    }
   });
  }

  $.each($.dynaCloud.cloud, function(i, n) {
   cl[cl.length] = n;
  });

  if ($.dynaCloud.sort) {
   cl.sort(function(a, b) {
    if (a.count == b.count) {
     return a.el < b.el ? -1 : (a.el == b.el ? 0 : 1);
    }
    else {
     return a.count < b.count ? 1 : -1;
    }
   });
  }

  var out;
  if ((out = $("#dynacloud")).length == 0) {
   $("body").append('<p id="dynacloud"><\/p>');
   out = $("#dynacloud");
  }

  out.empty();

  var l = $.dynaCloud.max == -1 ? cl.length : Math.min($.dynaCloud.max, cl.length);

  for (var i = 0; i < l; ++i) {
   out.append("<a href='#" + cl[i].el + "' style='font-size: " + Math.ceil((cl[i].count / max) * 4) + "em'><span>" + cl[i].el + "<\/span><\/a> &nbsp; ");
  }

  $("#dynacloud a").each(function() {
   $(this).click(function() {

    if ($.dynaCloud.single) {
     $("span.highlight").each(function() {
      this.parentNode.replaceChild(this.firstChild, this).normalize();
     });
    }

    var text = $(this).text().toUpperCase();
    $("*[@class*=dynacloud]").each(function() { $.highlight(this, text); });
    return false;
   });
  });

  //alert("Took " + (new Date().getTime() - now) + " ms");

 });
};
