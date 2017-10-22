from __future__ import unicode_literals
import uuid
import os
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import formats
from django.utils import timezone


def get_object_by_uuid_or_404(model, uuid_pk):
    """
    Calls get_object_or_404(model, pk=uuid_pk)
    but also prevents "badly formed hexadecimal UUID string" unhandled exception
    """
    try:
        uuid.UUID(uuid_pk)
    except Exception as e:
        raise Http404(str(e))
    return get_object_or_404(model, pk=uuid_pk)


def format_datetime(dt, include_time=True):
    """
    Apply datetime format suggested for all admin views.

    Here we adopt the following rule:
    1) format date according to active localization
    2) append time in military format
    """

    if dt is None:
        return ''

    # convert to localtime
    try:
        dt = timezone.localtime(dt)
    except ValueError:
        # Probably 'astimezone() cannot be applied to a naive datetime'
        pass

    text = formats.date_format(dt, use_l10n=True, format='SHORT_DATE_FORMAT')
    if include_time:
        text += dt.strftime(' %H:%M:%S')
    return text


def remove_file_and_cleanup(filepath):
    """
    Removes specified file, than it's folder if left empty
    """
    folder = os.path.dirname(filepath)
    # remove file
    if os.path.isfile(filepath):
        os.remove(filepath)
    # finally, remove folder if empty
    if os.path.isdir(folder) and len(os.listdir(folder)) <= 0:
        os.rmdir(folder)
