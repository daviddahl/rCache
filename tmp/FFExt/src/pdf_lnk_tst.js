var documentScraper = {
  
 links: function(){
    //var wndw=document.commandDispatcher.focusedWindow;
    var wndw=document;
    var links=wndw.getElementsByTagName("A");
    return links;
  },

 link_subset: function(links,regex){
    //var re = /~*.pdf$/;
    var pdfs = new Array();
    for (var i = 0; i < links.length; i++){
      if (regex.test(links[i].href)){
	pdfs.push(links[i]);
      }
    }
    return pdfs;
  },

 run: function(){
    var pdf_regex = /~*.pdf$/;
    var doc_regex = /~*.doc$/;
    var pg_links = documentScraper.links();
    var docs = documentScraper.link_subset(pg_links,doc_regex); 
    var pdfs = documentScraper.link_subset(pg_links,pdf_regex);
    var matched_links = {'pdfs':pdfs,'docs':docs};
    return matched_links;
  },

 report: function(matched_links){
    //var wndw=document.commandDispatcher.focusedWindow;
    var wndw=document;
    var myreportdiv = wndw.createElement("DIV");
    var docul = wndw.createElement("UL");
    var pdful = wndw.createElement("UL");
    var matched_links = documentScraper.run();

    for (var i = 0; i < matched_links['pdfs'].length; i++){
      
      var pdfli = wndw.createElement("LI");
      pdfli.innerHTML = matched_links['pdfs'][i].href;
      pdful.appendChild(pdfli);
    }

    for (var i = 0; i < matched_links['docs'].length; i++){
      var docli = wndw.createElement("LI");
      docli.innerHTML = matched_links['docs'][i].href;
      docul.appendChild(docli);
    }

    myreportdiv.appendChild(pdful);
    myreportdiv.appendChild(docul);

    var body = wndw.getElementsByTagName("BODY");

    if (body.length > 0){
      body[0].appendChild(myreportdiv);
    } else {
      alert("no body");
    }
  }
 
};
