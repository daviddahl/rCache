var recentGrid = {
    init : function(){
    // some data yanked off the web
    var myData = [[472, "no title, tags: Iran,India,Foreign Policy,neocon", "http://128.241.192.81/2006/03/lamerica.html", "2006-03-10 11:59:35"], [471, "\n      Shock and Awe; the Sequel\n", "http://www.opednews.com/maxwrite/print_friendly.php?p=opedne_mike_whi_060308_shock_and_awe_3b_the_s.htm", "2006-03-10 11:57:19"], [470, "no title, tags: Iraq,Security,Resistence", "http://128.241.192.81/2006/03/three-years-after-baghdad-today.html", "2006-03-10 11:54:41"], [469, "no title, tags: data mining,NSA,Security", "http://www.wired.com/news/columns/1,70357-0.html", "2006-03-10 11:44:07"], [468, "\n      Journal of Turkish Weekly - Iran said to step up plans for\n      Shahab missiles\n", "http://www.turkishweekly.net/printer-friendly/printerfriendly.php?type=news&id=27239", "2006-03-10 09:57:52"], [467, "no title, tags: Google,Search Engines", "http://intermaweb.net/index.php/2006/03/05/information-idol-how-google-is-making-us-stupid/", "2006-03-09 22:23:24"], [466, "\n      BBC NEWS | Americas | Bush damaged by political iceberg\n", "http://newsvote.bbc.co.uk/mpapps/pagetools/print/news.bbc.co.uk/2/hi/americas/4791248.stm", "2006-03-09 20:54:49"], [465, "this is a test", "http://ddahl.com", "2006-03-09 20:47:10"], [464, "test", "http://test.com", "2006-03-09 20:44:06"], [463, "test", "http://test.com", "2006-03-09 20:42:10"], [462, "java script goodness", "http://www.javascriptkit.com/jsref/", "2006-03-09 20:40:57"], [461, "\n      Lateline - 10/03/2006: Iran, US nuclear tensions deepen\n", "http://www.abc.net.au/lateline/content/2006/s1588223.htm", "2006-03-09 13:47:28"], [460, "\n      Lighttpd For Both SSL And Non-SSL - ArchWiki\n", "http://wiki.archlinux.org/index.php/Lighttpd_For_Both_SSL_And_Non-SSL", "2006-03-09 13:04:45"], [458, "\n      Edge: JARED DIAMOND - HOW TO GET RICH [page 2]\n", "http://www.edge.org/3rd_culture/diamond_rich/rich_p2.html", "2006-03-09 11:06:43"], [457, "\n      PINR - Bulgaria and Turkey Move to Secure Accession to the\n      E.U.\n", "http://www.pinr.com/report.php?ac=view_printable&report_id=451&language_id=1", "2006-03-09 10:49:34"], [456, "U.S. stuck with few options in Iraq", "http://seattletimes.nwsource.com/cgi-bin/PrintStory.pl?document_id=2002844798&zsection_id=2002107549&slug=iraqoptions05&date=20060305", "2006-03-09 09:47:09"], [455, "\n      Informed Comment\n    \n      Juan Cole * Informed Comment *\n", "http://www.juancole.com/2006/03/khalilzad-meets-al-hakim-reuters.html", "2006-03-09 09:37:50"], [454, "\n      State Your Position \u00c3\u0082\u00c2\u00bb Blog Archive \u00c3\u0082\u00c2\u00bb Twilight of\n      the Hegemony\n", "http://www.stateyourposition.com/2006/03/05/twilight-of-the-hegemony/", "2006-03-08 12:08:47"], [453, "\n      911Truth.org ::::: The 9/11 Truth Movement\n", "http://www.911truth.org/article.php?story=20050521102328420", "2006-03-08 09:31:08"], [452, "no title, tags: Wirt Walker,Bush,911,WTC", "http://www.spitfirelist.com/f431.html", "2006-03-07 22:09:55"]];
    var dataModel = new YAHOO.ext.grid.DefaultDataModel(myData);
    var sort = YAHOO.ext.grid.DefaultColumnModel.sortTypes;
    
    var colModel = new YAHOO.ext.grid.DefaultColumnModel([
							  {header: "ID", width: 200, sortable: true, sortType: sort.asUCString}, 
							  {header: "Name", width: 75, sortable: true, renderer: money}, 
							  {header: "Url", width: 75, sortable: true, renderer: change}, 
							  {header: "Date", width: 85, sortable: true, renderer: italic}
							  ]);
    var grid = new YAHOO.ext.grid.Grid('example-grid', dataModel, colModel);
    grid.render();
    grid.getSelectionModel().selectFirstRow();
  }	
}

YAHOO.ext.EventManager.onDocumentReady(recentGrid.init, Recent, true);
