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

RQ_PREFIX = "test"
RQ_QUEUES = setup_rq_queues(RQ_PREFIX)

RQ_SHOW_ADMIN_LINK = True
DJANGOTASK_LOG_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', 'protected', 'test_tasklog'))
DJANGOTASK_ALWAYS_EAGER = True
DJANGOTASK_JOB_TRACE_ENABLED = True
