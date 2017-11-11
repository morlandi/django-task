(function($) {

    $(document).ready(function() {
        var body = $('body');
        if (body.hasClass('change-list') || body.hasClass('grp-change-list')) {
            update_tasks(1000);
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
        var incomplete_task_ids = [];
        $('.task_status[data-task-complete="0"]').each(function(index, item) {
            incomplete_task_ids.push($(item).data('task-id'));
        });
        if (incomplete_task_ids.length > 0) {

            $.ajax({
                url: '/django_task/info/',
                data: {'ids[]': incomplete_task_ids},
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
        var row = $('#result_list .task_status[data-task-id="' + item.id + '"').closest('tr');
        if (row.length) {
            $(row).find('.field-started_on_display').html(item.started_on_display);
            $(row).find('.field-completed_on_display').html(item.completed_on_display);
            $(row).find('.field-duration_display').html(item.duration_display);
            $(row).find('.field-status_display').html(item.status_display);
            $(row).find('.field-progress_display').html(item.progress_display);
            for (key in item.extra_fields) {
                $(row).find('.field-' + key).html(item.extra_fields[key]);
            }
        }
    }

})(django.jQuery);
