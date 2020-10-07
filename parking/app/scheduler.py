import logging
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
formatter = logging.Formatter(
    '[%(asctime)s - %(levelname)s] %(module)s - %(name)s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
    )

class MyBatches():

    def start(self):
        if settings.DEBUG:
            set_logger=logging.getLogger('apscheduler')
            set_logger.setLevel(logging.WARNING)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            set_logger.addHandler(stream_handler)

            try:
                scheduler.start()
                set_logger.info('BackgroundScheduler is Started!')
            except:
                set_logger.error('BackgroundScheduler is Not Started!')
