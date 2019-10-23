from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    Usage:
        {% get_verbose_field_name test_instance "name" %}

    Thanks to pankaj28843,
    https://stackoverflow.com/questions/14496978/fields-verbose-name-in-templates#14498938
    """
    return instance._meta.get_field(field_name).verbose_name.title()


def _list_fieldnames(task, excluded):
    """
    Lists all fields on given "task" Model object,
    getting rid of those listed in "excluded", if any.
    Parameters:
        excluded: a string containing a (possibly empty) list of fieldnames to be excluded, separated by ','
    Returs:
        a list of fieldnames
    """
    fieldnames = []
    if task:

        # start with all fields, but also insert "duration"
        fieldnames = []
        for f in task._meta.fields:
            fieldnames.append(f.name)
            if f.name == "completed_on":
                fieldnames.append("duration")

        # remove excluded
        excluded = [f.strip() for f in excluded.split(',') if f.strip()]
        fieldnames = [f for f in fieldnames if f not in excluded]

    return fieldnames


@register.filter
def render_task_column_names_as_table_row(task, excluded=""):
    """
    Returns a sequence of "<th>" columns for rendering the given task fieldnames in an HTML table
    """
    fieldnames = _list_fieldnames(task, excluded)
    row = ''
    for fieldname in fieldnames:
        # If a FIELDNAME_display() method is available, get it's "short_description" value
        renderer = getattr(task, fieldname + '_display', None)
        if renderer is not None:
            label= getattr(renderer, 'short_description', fieldname)
        else:
            # Else, use the verbose name of the field
            try:
                label = get_verbose_field_name(task, fieldname)
            except:
                label = fieldname
        row += '<th class="column-{}">{}</th>'.format(fieldname, label)

    return mark_safe(row)


@register.filter
def render_task_as_table_row(task, excluded=""):
    """
    Returns a sequence of "<td>" items for rendering the given task contents in an HTML table;
    a suitable css class is also assigned to each item, to update later the HTML table
    during task progress using the javascript update_tasks() helper
    """
    fieldnames = _list_fieldnames(task, excluded)
    row = ''
    for fieldname in fieldnames:
        # If a FIELDNAME_display() method is available, use it for rendering
        renderer = getattr(task, fieldname + '_display', None)
        if renderer is not None:
            value = renderer()
            css_class = 'field-{}_display'.format(fieldname)
        else:
            # Else,
            value = getattr(task, fieldname)
            css_class = 'field-{}'.format(fieldname)
        row += '<td class="{}">{}</td>'.format(css_class, value)

    return mark_safe(row)
