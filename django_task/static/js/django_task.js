(function($) {

    $(document).ready(function() {
        var body = $('body');
        if (body.hasClass('change-list') || body.hasClass('grp-change-list')) {
            $('.field-log_link_display a.logtext').on('click', view_log_text);
            update_tasks(1000);
        }
        if (body.hasClass('change-form') || body.hasClass('grp-change-form')) {
            // hide "save and continue" button from submit row
            $('.submit-row button[name="_continue"]').hide();
        }
    });

    var update_tasks_timer = null;

    function getCookie(name) {
        var value = '; ' + document.cookie,
            parts = value.split('; ' + name + '=');
        if (parts.length == 2) return parts.pop().split(';').shift();
    }

    function update_tasks(autorepeat_interval) {

        console.log('update_tasks() ...');

        // clear one-shot timer
        if (update_tasks_timer != null) {
            clearTimeout(update_tasks_timer);
            update_tasks_timer = null;
        }

        // Collect incomplete taks
        var incomplete_tasks = [];
        $('.task_status[data-task-complete="0"]').each(function(index, item) {
            incomplete_tasks.push({
                id: $(item).data('task-id'),
                model: $(item).data('task-model')
            });
        });
        //console.log('incomplete tasks: %o', incomplete_tasks);

        if (incomplete_tasks.length > 0) {

            $.ajax({
                url: '/django_task/info/',
                data: JSON.stringify(incomplete_tasks),
                cache: false,
                crossDomain: true,
                type: 'post',
                dataType: 'json',
                //contentType: 'application/json; charset=utf-8',
                headers: {"X-CSRFToken": getCookie('csrftoken')}
            }).done(function(data) {
                var repeat = false;
                $.each(data, function(index, item) {
                    if (!item.completed) {
                        repeat = true;
                    }
                    update_task_row(item);
                });
                if (repeat) {
                    // re-arm timer
                    if (autorepeat_interval > 0) {
                        setTimeout(function() { update_tasks(autorepeat_interval); }, autorepeat_interval);
                    }
                }
            }).fail(function(jqXHR, textStatus) {
                console.log('update_tasks() ERROR: %o', jqXHR);
                // re-arm timer
                if (autorepeat_interval > 0) {
                    setTimeout(function() { update_tasks(autorepeat_interval); }, autorepeat_interval);
                }
            });
        }
    }

    function update_task_row(item) {
        var row = $('#result_list .task_status[data-task-id="' + item.id + '"]').closest('tr');
        if (row.length) {
            $(row).find('.field-started_on_display').html(item.started_on_display);
            $(row).find('.field-completed_on_display').html(item.completed_on_display);
            $(row).find('.field-duration_display').html(item.duration_display);
            $(row).find('.field-status_display').html(item.status_display);
            $(row).find('.field-progress_display').html(item.progress_display);
            $(row).find('.field-log_link_display').html(item.log_link_display);
            for (key in item.extra_fields) {
                $(row).find('.field-' + key).html(item.extra_fields[key]);
            }
            $(row).find('.field-log_link_display a.logtext').on('click', view_log_text);
        }
    }

    function view_log_text(event) {
        var url = $(event.target).attr('href');
        $.ajax({
            type: 'GET',
            url: url,
            success: function(data, textStatus, jqXHR) {
                alert(data);
            }
        });
        return false;
    }

})(django.jQuery);
