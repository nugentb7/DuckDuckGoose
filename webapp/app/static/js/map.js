var mymap = L.map("map").setView([0, 0], 13);

let rasterBounds = [
    [37.371796016, -107.431244616], 
    [37.404768832, -107.382423016]
]

let locationIcon = L.Icon.extend({
    options: {
        iconSize:     [10, 10],
        iconAnchor:   [22, 94],
        shadowAnchor: [4, 62],
        popupAnchor:  [-3, -76]
    }
});

let style;
let sensorMarkers = [];
let wasteMarkers = [];
let points;
let bounds;
let wasteLayer;
let sensorLayer;
let maxZoom;

let imageUrl = "/static/images/waterways_map.jpg",
    imageBounds = rasterBounds;
let ogMap = L.imageOverlay(imageUrl, imageBounds, { "opacity" : .45 });


let imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    opacity: .70
});
imagery.addTo(mymap);

var grayMap = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 19
});


let layerControl = L.control.layers(
    {}, 
    {},
    { "collapsed" : false }
).addTo(mymap);

$.get(
    "/rest/locations/", 
    function(data) {
        points = L.geoJSON(data, {
            style: function(feature) {
                return feature["style"];
            },
            onEachFeature: function(feature) {
                icon = feature["icon"];

                var thisIcon = L.icon({
                    iconUrl: icon["iconUrl"],
                    iconSize: icon["iconSize"],
                    iconAnchor: [0, 10],
                });


                let marker = L.marker(
                    icon["latlng"], { "icon" : thisIcon }
                );
                marker.bindTooltip(
                    feature["properties"]["display"], {
                        permanent: true, className: "location-label", direction: "top", offset: [12, 0]
                    }
                );

                marker.bindPopup(
                    "<span>Some stuff about <b>"+feature["properties"]["display"]+"</b></span>"
                );
                if (feature["properties"]["type"]["name"] === "WASTE") {
                    wasteMarkers.push(marker);
                } else {
                    sensorMarkers.push(marker);
                }
                
                //marker.addTo(mymap);
            }                
        });

        bounds = points.getBounds();
        mymap.fitBounds(bounds);
        mymap.setMaxBounds(bounds.pad(1));
        
        mymap.setMinZoom(mymap.getZoom());

    }
).done(function() {
    sensorLayer = L.layerGroup(sensorMarkers);
    wasteLayer = L.layerGroup(wasteMarkers);
    sensorLayer.addTo(mymap);
    wasteLayer.addTo(mymap);
    layerControl.addOverlay(sensorLayer, "Sensors");
    layerControl.addOverlay(wasteLayer, "Kasios Dumping Location");
    layerControl.addOverlay(ogMap, "Original Map");
});

$("#measure-search").select2({
    "ajax": {
        "url": "/rest/measure"
    },
    "theme": "bootstrap"
});

$("#sensor-search").select2({
    "theme": "bootstrap"
});