from .settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "77777777777777777777777777777777777777777777777777"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'testdb.sqlite3'),
        'NAME': ':memory:',
    }
}

#INSTALLED_APPS.remove('easyaudit')

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'public', 'test_media'))

THUMBNAIL_DEBUG = True

INSTANCE_PREFIX = "test"
QUEUE_DEFAULT = INSTANCE_PREFIX + '_default'
QUEUE_LOW = INSTANCE_PREFIX + '_low'
QUEUE_HIGH = INSTANCE_PREFIX + '_high'

RQ_QUEUES = {
    QUEUE_DEFAULT: {
        'URL': REDIS_URL,
        #'PASSWORD': 'some-password',
        #'DEFAULT_TIMEOUT': 5 * 60,
        'DEFAULT_TIMEOUT': -1,  # -1 means infinite
    },
    QUEUE_LOW: {
        'URL': REDIS_URL,
        #'ASYNC': False,
        'DEFAULT_TIMEOUT': 10 * 60,
    },
    QUEUE_HIGH: {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 500,
    },
}

settings_echo('', title='RQ_QUEUES (overridden)')
for rq_queue_key, rq_queue_value in RQ_QUEUES.items():
    settings_echo(rq_queue_value, title='- ' + rq_queue_key)

RQ_SHOW_ADMIN_LINK = True
DJANGOTASK_LOG_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'protected', 'test_tasklog'))
DJANGOTASK_ALWAYS_EAGER = True
DJANGOTASK_JOB_TRACE_ENABLED = True
