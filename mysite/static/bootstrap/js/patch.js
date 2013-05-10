
$(document).ready(function(){
	$("#language_selector").click(function() {
	$('#language_form :input[name="language"]').val($(this).attr("data-language-code"));
	$('#language_form').submit();
	});
});