function createCatalog(){     
    var obj = {
        "name": "DEA Production",
        "type": "group",
        "preserveOrder": true,
        "items": [

        ] 
    };
    var new_catalog = [];
    // load reference json
    $.getJSON("http://ec2-52-64-97-251.ap-southeast-2.compute.amazonaws.com/js/featurereference.json", function(data){

        var items = [];
        $.each( data, function( key, val ) {
             console.log(key, val);
        });


        // beginning of get
        // $.get('https://ows.dea.ga.gov.au/?service=WMS&request=GetCapabilities&version=1.3.0&tiled=true')
        // .done(
        //     function (xml) {
        //         var $xml = $(xml);
        //         $xml.find('Layer').find('Layer[queryable!="1"]').each(function(){
        //                 var folder_title = $(this).find('Title').first().text();
        //                 var new_folder = {};
        //                 new_folder['name'] = folder_title;
        //                 new_folder['type'] = 'group';
        //                 new_folder['preserveOrder'] = true;
        //                 new_folder['items'] = [];
        //                 new_catalog.push(new_folder);
        //             $(this).find('Layer[queryable="1"]').each(function(){
        //                 var name = $(this).find('Name').first().text();
        //                 var title = $(this).find('Title').first().text();
        //                 var new_item = {};
        //                 new_item['name'] = title;
        //                 new_item['type'] = 'wms';
        //                 new_item['layers'] = name;
        //                 new_item['url'] = 'https://ows.dea.ga.gov.au/';
        //                 new_item['linkedWcsUrl'] = 'https://ows.dea.ga.gov.au/';
        //                 new_item['linkedWcsCoverage'] = name;
        //                 new_item["ignoreUnknownTileErrors"] =true;
        //                 new_item["chartType"]= "momentPoints";
        //                 new_item["chartColor"] = "white";
        //                 new_item["opacity"] = 1;
        //                 if (referenceJson[name]){

        //                 }
        //                 new_folder['items'].push(new_item);
        //             });
        //             obj['items'].push(new_folder);
    
        //         });
        //         $('#obj').text(JSON.stringify(obj, null, 4));
                
        //     }
        // );
        // end of get
    });
}
