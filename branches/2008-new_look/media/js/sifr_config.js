var bulmerMT = {
  src: '/media/swf/bulmerMT.swf',
};
var bulmerMTSEMI = {
  src: '/media/swf/bulmerMTSEMI.swf'
};
var bembo = {
  src: '/media/swf/bembo.swf',
};
var bemboSEMI = {
  src: '/media/swf/bemboSEMI.swf'
};


sIFR.activate(bembo,bemboSEMI,bulmerMT,bulmerMTSEMI);

sIFR.replace(bulmerMT, {
  	selector: 'h1'
    ,wmode:'transparent'
    ,forceClear:'true'
    ,forceWidth:'true'
    ,fitExactly:'true'
    ,repaintOnResize:'false'
    ,offsetTop:'-4'
    ,offsetLeft:'0'
    ,tuneHeight:'-5'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'leading':'-14','font-size':'43','color':'#272115','letter-spacing':-2,'background-color':'#E2DEBF','margin-left':0,'margin-right':0,'text-transform':'none'},
        'a' : {'color': '#272115','text-decoration': 'none'},
        'a:hover' : {'color': '#272115'}
    }
});


sIFR.replace(bulmerMT, {
  	selector: '.home-title'
    ,wmode:'transparent'
    ,forceClear:'true'
    ,forceSingleLine:'true'
    ,forceWidth:'true'
    ,fitExactly:'true'
    ,repaintOnResize:'false'
    ,offsetTop:'-8'
    ,offsetLeft:'0'
    ,tuneHeight:'-8'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'leading':'-14','font-size':'34','color':'#ffffff','letter-spacing':-1,'background-color':'#3F341D','margin-left':0,'margin-right':0,'text-transform':'none','display':'block','text-align':'center'},
        'a' : {'color': '#ffffff','text-decoration': 'none'},
        'a:hover' : {'color': '#E2DEBF'}
    }
});
sIFR.replace(bulmerMT, {
  	selector: '.home-subtitle'
    ,wmode:'transparent'
    ,forceClear:'true'
    ,forceSingleLine:'true'
    ,forceWidth:'true'
    ,fitExactly:'true'
    ,repaintOnResize:'false'
    ,offsetTop:'0'
    ,offsetLeft:'0'
    ,tuneHeight:'-8'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'font-size':'11','color':'#E2DEBF','letter-spacing':6,'background-color':'#3F341D','margin-left':0,'margin-right':0,'text-transform':'uppercase','display':'block','text-align':'center'}
    }
});
