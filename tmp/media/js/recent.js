var myColumnHeaders = [
		       {key:"rcacheid", text:"Id",sortable:true},
		       {key:"name", text:"Title",sortable:true},
		       {key:"date",text:"rCached",sortable:true}
		       ];

var myColumnSet = new YAHOO.widget.ColumnSet(myColumnHeaders);

// Point to a local or proxy URL
var myDataSource = new YAHOO.util.DataSource("/recent_xhr/");

// Set the responseType as JSON
myDataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;

// Define the data schema
myDataSource.responseSchema = {
    resultsList: "entries_db.items", // Dot notation to results array
    fields: ["rcacheid","name","date"] // Field names
};


