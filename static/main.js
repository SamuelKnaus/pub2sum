jQuery("#summarize-files").click(function () {
    jQuery(this).html("<span class=\"spinner-grow spinner-grow-sm\" role=\"status\" aria-hidden=\"true\"></span>&nbsp;Analyzing, please wait...")
});

jQuery("pre").after().click(function () {
    console.log(jQuery(this).text())
})