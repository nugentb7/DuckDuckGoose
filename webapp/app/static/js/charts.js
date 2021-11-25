import * as d3 from "d3"

function generateDataUri() {
    let searchUri = "/rest/readings";
    let params = [];

    let measures = [];
    $.each($("#measure-search").val(), function(i, val) {
        measures.push(val);
    });
    if (measures.length) {
        params.push("measures=" + JSON.stringify(measures));
    }

    let locations = [];
    $.each($("#sensor-search").val(), function(i, val) {
        locations.push(val);
    });
    if (locations.length) {
        params.push("locations=" + JSON.stringify(locations));
    }

    let startDate = $("#start-date").val()
        , endDate   = $("#end-date").val()
    ;
    
    if (startDate) {
        params.push("start_date=" + startDate);
    }
    if (endDate) {
        params.push("end_date=" + endDate);
    }

    if (params.length) {
        searchUri += ("?" + params.join("&"));
    }
    return searchUri;
}


$(function() {
    $("#measure-search").select2({
        "theme": "bootstrap", 
        "maximumSelectionLength": 2
    });
    
    $("#sensor-search").select2({
        "maximumSelectionLength": 2, 
        "theme": "bootstrap"
    });
    
    $("#chart-type").select2({
        "theme": "bootstrap"
    });

    $("#generate").click(function() {
        d3.json(generateDataUri(), function(data) {
            chart = LineChart(data["results"], {
                x: data => data.sample_date,
                y: data => data.value,
                z: data => data.location.display,
                yLabel: "Test",
                width: 500,
                height: 500,
                color: "steelblue",
            });
            console.log(chart);
        });    
    });
});


