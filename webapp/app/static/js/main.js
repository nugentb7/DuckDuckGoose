$(".pane-switch").click(function() {
    $(this).prop("disabled", true);
    $($(this).data("target")).removeClass("d-none");
    $($(this).data("switch")).addClass("d-none");
    $($(this).data("switch") + "-btn").prop("disabled", false);
}); 