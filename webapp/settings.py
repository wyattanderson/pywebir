import os

DEBUG = True
STYLUS_PLUGINS = 'nib'

REDIS_HOST='192.168.1.148'
REDIS_PORT=6379
REDIS_SETTINGS_KEY = 'pywebir_settings'

CELERY_BROKER_URL='redis://{host}:{port}'.format(
        host=REDIS_HOST,
        port=REDIS_PORT)
CELERY_RESULT_BACKEND=CELERY_BROKER_URL
CELERYD_CONCURRENCY=1

SKIP_IR = os.getenv('SKIP_IR', 'false').lower() == 'true'
