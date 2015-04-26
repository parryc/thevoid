$(document).ready(function(){
  //CSRF setup from Flask-WTF docs
  var csrftoken = $('meta[name=csrf-token]').attr('content');
  var queryResults = Handlebars.templates['query-results'];

  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
    }
  });

  var query = function(evt) {
    console.log('here');
    var query = $('#query').val()
        ,data = {}
        ;
    if(query === '') {
      query = $('.search #brewery').val() + ' ' + $('.search #name').val()
    }

    data = {'query':query}

    $('#query-results').text('Searching...');
    // strip the brewery name from the "name", also strip "brewery" "brewing" etc.
    $.ajax({
      type: 'POST',
      url: '/beers/query',
      data: JSON.stringify(data),
      contentType: 'application/json;charset=UTF-8',
      success: function(results) {
        if(results.no_hits) { 
          $('#query-results').text('Nothing to see here.'); 
        }
        console.log(results)
        $('#query-results').html(queryResults(results));
      }
    });

    console.log(data);
  }


  $('#query').on("input",$.debounce(query, 500));


});