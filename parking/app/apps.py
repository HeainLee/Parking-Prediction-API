import logging
from django.apps import AppConfig
from django.conf import settings

from . import scheduler


class AppConfig(AppConfig):
    # logging.basicConfig()
    logging.getLogger('').setLevel(logging.INFO)

    name = 'app'
    logging.info(f'    > SCHEDULER_AUTOSTART: {settings.SCHEDULER_AUTOSTART}')
    logging.info(f"    > scheduler.scheduler: {scheduler.scheduler}")
    # <apscheduler.schedulers.background.BackgroundScheduler object at 0x123b5fe80>
    logging.info(f"    > running?: {scheduler.scheduler.running}", ) # -> False

    batch = scheduler.MyBatches()
    logging.info(f'    > batch: {batch}')
    # ['add_batch', 'job_function', 'kill_scheduler', 'start']
    if settings.SCHEDULER_AUTOSTART:
        batch.start()

    logging.info(f"    > running?: {scheduler.scheduler.running}") # -> True
    # view 에서 dj_scheduler를 받아서 add_job 또는 remove_job을 시행
    dj_scheduler = scheduler.scheduler
