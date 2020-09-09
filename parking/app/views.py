from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import os
import json
import requests
from datetime import datetime
from django_apscheduler.jobstores import register_events
from apscheduler.schedulers import SchedulerAlreadyRunningError

from .apps import AppConfig
from .train_model import parking_model


def job_function():
    # print('Tick! The time is: %s' % datetime.now())
    url = "http://10.1.1.61:8002/analyticsModule/algorithm/1"
    response = requests.get(url)
    # print("상태:", response.status_code)


def model_batch_function(model_id):
    # print('Tick! The time is: %s' % datetime.now())
    url = "http://10.1.1.61:8002/analyticsModule/algorithm/1"
    response = requests.get(url)
    print("상태:", response.status_code)

def model_batch_function_edit(model_id):
    # print('Tick! The time is: %s' % datetime.now())
    url = "http://10.1.1.61:8002/analyticsModule/algorithm/" + str(model_id)
    response = requests.get(url)
    print("상태:", response.status_code)

class ParkingModelView(APIView):
    # 주차장 모델 생성 결과 조회 
    def get(self, request):
        try:
            if request.GET.get('p_id', False):
                p_id = request.GET['p_id']
                filename = request.GET['filename']
                model_path = "/Users/heain/parking_prediction_api/parking/model"

                if filename.endswith('.txt'):
                    load_path = os.path.join(model_path, str(p_id), filename)
                    with open(load_path, 'r', encoding='UTF-8') as f:
                        get_info=json.loads(f.read())
                    model_info = dict(model_info=get_info)

                    final_result = {}
                    final_result['path'] = load_path
                    final_result['result'] = model_info
                    return Response(final_result, status=status.HTTP_200_OK)

                elif filename.endswith('.model'):
                    return Response('모델조회불가', status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                query_key = ["dirname", "filename"]
                # TODO 경로 변경 
                model_path = "/Users/heain/parking_prediction_api/parking/model"

                result_ = {}
                result_["path"] = str
                result_['result'] = []
                get_infos = {}
                for dirpath, dirnames, filenames in os.walk(model_path):
                    print("dirpath:", dirpath)
                    # dirnames.sort()

                    if dirpath == model_path:
                        result_['path'] = dirpath
                        # get_dir = dirnames # ['1', '2',....]
                    else:
                        get_info = {}
                        dir_name = os.path.split(dirpath)[1]
                        get_info['files'] = filenames
                        get_infos[dir_name] = get_info

                # get_infos = sorted(get_infos.items())
                result_['result'] = get_infos
                return Response(result_, status=status.HTTP_200_OK)

        except FileNotFoundError as e:
            error_return = {}
            error_return["error"] = 'FileNotFoundError'
            error_return["message"] = e.strerror
            return Response(error_return, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_return = {}
            error_return["error"] = e.__class__.__name__
            error_return["message"] = str(e)
            return Response(error_return, status=status.HTTP_400_BAD_REQUEST)

    # 주차장 모델 생성
    def post(self, request):
        # 모델 생성하고 결과 반환
        # TODO 모델 생성 클래스 
        result = parking_model()
        result = True
        if result:
            return Response('모델이 생성을 요청했습니다.', status=status.HTTP_200_OK)
        else:
            return Response('모델 생성에 실패했습니다.', status=status.HTTP_400_BAD_REQUEST)


class ParkingModelDetailView(APIView):

    def patch(self, request, pk):
        from apscheduler.jobstores.base import ConflictingIdError
        from apscheduler.jobstores.base import JobLookupError

        """
        모델 배치 돌리는 방법 : patch 메소드로 pk에 해당하는 모델 배치로 실행시키기 
        + 옵션 0 : 배치상태 : start, stop, get 택 1
        + 옵션 1 : 실행주기 : minutes 설정 start_data 설정 end_date 설정
        + 옵션 2 : 실행방식 : start / stop (status는 get 메소드로 대신함)
        """
        # 모델 id의 배치 실행시키기 
        if request.GET['status'] == 'start':
            get_scheduler = AppConfig.dj_scheduler
            try:
                # get_scheduler.add_job(job_function, 'interval', seconds=30, id=request.GET['job_id'])
                # get_scheduler.add_job(model_batch_function, 'interval', minutes=1, id=pk, args=[pk])
                # TODO : 선택 옵션 파라미터로 받아서 수정
                get_scheduler.add_job(model_batch_function_edit, 'interval', minutes=1, id=pk, args=[pk])
            except ConflictingIdError as e:
                print(e)
                return Response(f'{pk} 모델은 이미 배치가 시작되었습니다.')
            return Response(f'{pk} 모델 배치를 시작합니다.')

        # 모델 id의 배치 정지시키기 
        elif request.GET['status'] == 'stop':
            get_scheduler = AppConfig.dj_scheduler
            # print(dir(get_scheduler))
            try:
                get_scheduler.remove_job(pk)
            except JobLookupError as e:
                print(e)
                return Response(str(e))
            return Response(f'{pk} 모델 배치를 종료합니다.')

        # 모델 id의 배치 수정하기
        elif request.GET['status'] == 'edit':
            get_scheduler = AppConfig.dj_scheduler
            try:
                # reschedule the job -> change its trigger
                # get_scheduler.reschedule_job(pk, trigger='interval', minutes=10)
                # TODO : 선택 옵션 파라미터로 받아서 수정
                get_scheduler.reschedule_job(pk, trigger='cron', minute='*/50') # Every 00 minutes
            except JobLookupError as e:
                print(e)
                return Response(str(e))
            return Response(f'{pk} 모델 배치를 수정합니다.')

        # 모델 id의 배치 상태 확인 
        elif request.GET['status'] == 'get':
            from django_apscheduler.models import DjangoJobExecution, DjangoJob
            batch_all = DjangoJob.objects.order_by('id')
            if not str(pk) in list(DjangoJob.objects.all().values_list("id", flat=True)):
                return Response(f'{pk} 모델 배치 정보가 존재하지 않습니다.')

            get_scheduler = AppConfig.dj_scheduler
            # list [<Job (id=2 name=job_function)>]
            print("get_jobs() : ", get_scheduler.get_jobs())
            print("print_jobs() : ", get_scheduler.print_jobs())
            for single_job in get_scheduler.get_jobs():
                if int(pk) == int(single_job.id):

                    return_dict = {}
                    for attr in ['id', 'func_ref', 'args', 'name', 'next_run_time', 'trigger']:
                        if attr != 'trigger':
                            return_dict[attr]=getattr(single_job, str(attr))
                        else:
                            return_dict['trigger'] = str(single_job.trigger)
                            return_dict['timezone'] = str(single_job.trigger.timezone)
                    return Response(return_dict)

            return Response(f'배치상태(status)를 지정해주세요: start, stop, status 중 택1')


