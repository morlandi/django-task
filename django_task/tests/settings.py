# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "77777777777777777777777777777777777777777777777777"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django_task",
]

SITE_ID = 1

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()


#
# RQ config
#

REDIS_URL = 'redis://localhost:6379/0'
#RQ_PREFIX = "myrq_"
RQ_PREFIX = ""
QUEUE_DEFAULT = RQ_PREFIX + 'default'
QUEUE_HIGH = RQ_PREFIX + 'high'
QUEUE_LOW = RQ_PREFIX + 'low'
#QUEUE_SCHEDULED = RQ_PREFIX + 'scheduled'

RQ_QUEUES = {
    QUEUE_DEFAULT: {
        'URL': REDIS_URL,
        #'PASSWORD': 'some-password',
        'DEFAULT_TIMEOUT': 360,
    },
    QUEUE_HIGH: {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 500,
    },
    QUEUE_LOW: {
        'URL': REDIS_URL,
        #'ASYNC': False,
    },
    # QUEUE_SCHEDULED: {
    #     'URL': REDIS_URL,
    # },
}

RQ_SHOW_ADMIN_LINK = True

DJANGOTASK_LOG_ROOT = ''
DJANGOTASK_JOB_TRACE_ENABLED = True
#DJANGOTASK_ALWAYS_EAGER = True
DJANGOTASK_REJECT_IF_NO_WORKER_ACTIVE_FOR_QUEUE = True
