import logging
from django.apps import AppConfig
from django.conf import settings

from . import scheduler


class AppConfig(AppConfig):
    logger = logging.getLogger('apps')
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(scheduler.formatter)
    logger.addHandler(stream_handler)

    name = 'app'
    logger.info(f'SCHEDULER_AUTOSTART: {settings.SCHEDULER_AUTOSTART}')
    logger.info(f"Scheculer Name: {type(scheduler.scheduler).__name__}")
    # <apscheduler.schedulers.background.BackgroundScheduler object at 0x123b5fe80>
    logger.debug(f"Is Scheculer Running?: {scheduler.scheduler.running}", ) # -> False

    batch = scheduler.MyBatches()
    # logger.info(f'batch: {type(batch).__name__}, {batch}')
    # ['add_batch', 'job_function', 'kill_scheduler', 'start']
    if settings.SCHEDULER_AUTOSTART:
        batch.start()
    logger.info(f"Is Scheculer Running?: {scheduler.scheduler.running}") # -> True
    # view 에서 dj_scheduler를 받아서 add_job 또는 remove_job을 시행
    dj_scheduler = scheduler.scheduler
