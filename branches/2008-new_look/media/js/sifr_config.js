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
var myriadCDBD = {
  src: '/media/swf/myriadCDBD.swf'
};

var tradecondBD = {
  src: '/media/swf/tradecondBD.swf'
};

var unvCOND = {
  src: '/media/swf/unvCOND.swf'
};



sIFR.activate(bembo,bemboSEMI,bulmerMT,bulmerMTSEMI);


sIFR.replace(bulmerMT, {
  	selector: '#text_content_boundry h1'
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
      '.sIFR-root': { 'leading':'-4','font-size':'43','color':'#272115','letter-spacing':-2,'background-color':'#ffffff','margin-left':0,'margin-right':0,'text-transform':'none'},
        'a' : {'color': '#272115','text-decoration': 'none'},
        'a:hover' : {'color': '#272115'}
    }
});

// sIFR.replace(myriadCDBD, {
//   	selector: '#detail_wrapper h3'
//     ,wmode:'transparent'
//     ,forceClear:'true'
//     ,forceWidth:'true'
//     ,fitExactly:'true'
//     ,repaintOnResize:'false'
//     ,offsetTop:'-2'
//     ,offsetLeft:'0'
//     ,tuneHeight:'-3'
//     ,tuneWidth:'3'
//     ,css: {
//       '.sIFR-root': { 'leading':'-1','font-size':'15','color':'#E68E3B','letter-spacing':0,'background-color':'#391608','margin-left':0,'margin-right':0,'text-transform':'none'},
//         'a' : {'color': '#272115','text-decoration': 'none'},
//         'a:hover' : {'color': '#272115'}
//     }
// });

sIFR.replace(myriadCDBD, {
  	selector: '#nav-wrap h4'
    ,wmode:'transparent'
    ,forceClear:'true'
    ,forceWidth:'true'
    ,fitExactly:'true'
    ,repaintOnResize:'false'
    ,offsetTop:'-2'
    ,offsetLeft:'0'
    ,tuneHeight:'-3'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'leading':'-1','font-size':'18','color':'#164354','letter-spacing':0,'background-color':'#D2E2E8','margin-left':0,'margin-right':0,'text-transform':'none'},
        'a' : {'color': '#272115','text-decoration': 'none'},
        'a:hover' : {'color': '#272115'}
    }
});




sIFR.replace(myriadCDBD, {
  	selector: '#global_page_title h1'
    ,wmode:'transparent'
    ,forceClear:'true'
    ,forceWidth:'true'
    ,fitExactly:'true'
    ,repaintOnResize:'false'
    ,offsetTop:'-3'
    ,offsetLeft:'0'
    ,tuneHeight:'-8'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'leading':'-14','font-size':'30','color':'#E68E3B','letter-spacing':-1,'background-color':'#391608','margin-left':0,'margin-right':0,'text-transform':'uppercase'},
        'a' : {'color': '#E68E3B','text-decoration': 'none'},
        'a:hover' : {'color': '#E68E3B'}
    }
});

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
      '.sIFR-root': { 'leading':'-14','font-size':'55','color':'#272115','letter-spacing':-2,'background-color':'#E2DEBF','margin-left':0,'margin-right':0,'text-transform':'none'},
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
    ,offsetTop:'-6'
    ,offsetLeft:'0'
    ,tuneHeight:'-8'
    ,tuneWidth:'3'
    ,css: {
      '.sIFR-root': { 'leading':'-14','font-size':'34','color':'#5FBAFF','letter-spacing':-1,'background-color':'#1F0F03','margin-left':0,'margin-right':0,'text-transform':'none','display':'block','text-align':'center'},
        'a' : {'color': '#5FBAFF','text-decoration': 'none'},
        'a:hover' : {'color': '#5FBAFF'}
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
      '.sIFR-root': { 'font-size':'11','color':'#E2DEBF','letter-spacing':6,'background-color':'#1F0F03','margin-left':0,'margin-right':0,'text-transform':'uppercase','display':'block','text-align':'center'}
    }
});
