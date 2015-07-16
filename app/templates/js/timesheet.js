$("#timesheet_submit").click(function(event){
  var url = $(this).attr('href');
  $('#timesheet').load(url);
  event.preventDefault();
});
