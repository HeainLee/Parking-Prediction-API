import logging
import requests
from datetime import datetime
from django.conf import settings
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, register_job


scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)


class MyBatches():

    def start(self):
        if settings.DEBUG:
            logging.basicConfig()
            logging.getLogger('apscheduler').setLevel(logging.DEBUG)
            scheduler.start()
            logging.info('BackgroundScheduler is Started!')

    # def add_batch(self, job_id, model_id):
    #     scheduler.add_job(self.job_function, 'interval', 
    #         seconds=5, id=job_id, args=[model_id])
    #     register_events(scheduler)
    #     print("Successfully add batch")
    #     return scheduler

    # def kill_scheduler(self, job_id):
    #     try:
    #         scheduler.remove_job(job_id)
    #         print("kill Scheduler job_id=",job_id)
    #     except JobLookupError as err:
    #         print("fail to stop Scheduler: {err}".format(err=err))
    #         return

    # def job_function(self, model_id):
    #     print('Tick! The time is: %s' % datetime.now())
    #     url = "http://localhost:8000/../algorithm/" + str(model_id)
    #     response = requests.get(url)
    #     print("status:", response.status_code)













