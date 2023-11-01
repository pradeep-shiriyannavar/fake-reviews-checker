$(document).ready(function() {
    $('#search-form').submit(function(event) {
      event.preventDefault();
      $('#results').html('');
      var url = $('#url-input').val();
      if (url === '') {
        $('#error-message').text('Please enter a URL');
        return;
      }
      $.ajax({
        url: '/search/',
        type: 'POST',
        data: {'url': url},
        success: function(response) {
          $('#results').html(response);
        },
        error: function() {
          $('#error-message').text('An error occurred. Please try again later.');
        }
      });
    });
  });
  