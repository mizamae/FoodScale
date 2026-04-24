$(document).ready(function(){
    var selects = $("select#id_timezone");
    if (selects.options.length > 0 && selects.val() == "") {
        var offset_minutes = new Date().getTimezoneOffset();
        var offset = 100 * offset_minutes / 60;
        var default_value = _first_timezone_match(selects, offset);
        selects.val(default_value);
    }
})

function _first_timezone_match(selects, offset) {
 var match = "";
 selects.find("option").each(function() {
  // ex: "(GMT-0500) America/New_York"
  if ($(this).text().indexOf(offset) > 0) {
   match = $(this).val();
  }
 });
 return match;
}