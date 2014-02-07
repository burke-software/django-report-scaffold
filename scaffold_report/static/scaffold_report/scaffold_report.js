jQuery(function($) { $.extend({
    form: function(url, data, method) {
        if (method == null) method = 'POST';
        if (data == null) data = {};

        var form = $('<form>').attr({
            method: method,
            action: url
         }).css({
            display: 'none'
         });

        var addData = function(name, data) {
            if ($.isArray(data)) {
                for (var i = 0; i < data.length; i++) {
                    var value = data[i];
                    addData(name + '[]', value);
                }
            } else if (typeof data === 'object') {
                for (var key in data) {
                    if (data.hasOwnProperty(key)) {
                        addData(name + '[' + key + ']', data[key]);
                    }
                }
            } else if (data != null) {
                form.append($('<input>').attr({
                  type: 'hidden',
                  name: String(name),
                  value: String(data)
                }));
            }
        };

        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                addData(key, data[key]);
            }
        }

        return form.appendTo('body');
    }
}); });

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function view_results(type) {
  var csrf_token = getCookie('csrftoken');
  var filters = $('#scaffold_active_filters .filter');
  var filter_data = []
  $('#preview_area').fadeOut();
  $(filters).each(function(key, value) { 
    var filter_dict = {
      'name': $(value).data('name'),
      'form': $(value).children('form.filter_form').serialize()
    }
    filter_data.push(filter_dict);
  })
  data_dict = {
    csrfmiddlewaretoken: csrf_token,
    data: JSON.stringify(filter_data),
  }
  
  if (type == 'preview') { // AJAX
    $.post(
      'view/?type=' + type,
      data_dict,
      function(data) {
        $('#preview_area').html(data);
        $('#preview_area').fadeIn();
      }
    );
  } else {
    $.form('view/?type=' + type, data_dict, 'POST').submit();
  }
}

function add_filter(select) {
    prepare_filter(select);
    view_results('preview');
    reindex_filters();
}

function prepare_filter(select) {
    var value = select.options[select.selectedIndex].value; // Outputs something like "TardyFilter"
    var form = $('#filter_copy_area .' + value).clone(true); // Set clone to true to duplicate event handler data as well (i.e. .click() action for delete-filter)

    $('#scaffold_active_filters').append(form);
    $('#add_new_filter').val('');
}

// Handle the deletion of filters. Mostly cosmetic.
$(document).ready(function() {
  $('.delete-filter').click(function() {
    $(this).parents('.filter').remove(); // Remove the whole block
  });
});

function reindex_filters() {
    var i = 0;
    $('#scaffold_active_filters .filter').each(function(index, value) { 
        $(value).attr('id', 'filter_' + i);
        $(value).children('form').children('input[name="filter_number"]').val(i);
        i += 1;
    });
}

$(function() {
  reindex_filters();
  $('#add_new_filter').val('');
  view_results('preview');
});

function process_errors(arr) {
  /* Process ajax error infomation
   * arr is an array generated in a django template */
  $('#scaffold_active_filters .filter').removeClass('filter_error');
  var i = 0;
  arr.forEach(function(value) {
    var filter_div = $('#scaffold_active_filters div#filter_'+value);
    filter_div.addClass('filter_error');
    filter_div.append(errors[i]);
    i += 1;
  });
}
