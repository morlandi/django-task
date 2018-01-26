from django.conf import settings

ALWAYS_EAGER = getattr(settings, 'DJANGOTASK_ALWAYS_EAGER', False)
LOG_ROOT = getattr(settings, 'DJANGOTASK_LOG_ROOT', None)
REDIS_URL = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
