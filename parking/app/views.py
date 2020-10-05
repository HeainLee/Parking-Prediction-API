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
from .test_model import parking_model_test, model_patch_apscheduler


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
                        get_info = json.loads(f.read())
                    model_info = dict(model_info=get_info)

                    final_result = {}
                    final_result['path'] = load_path
                    final_result['result'] = model_info
                    return Response(final_result, status=status.HTTP_200_OK)

                elif filename.endswith('.model'):
                    return Response('model file cannot be retrieved', 
                                    status=status.HTTP_400_BAD_REQUEST)
                    
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

                # 모델과 모델정보 별 재정렬
                sort_final_dict = {}
                for p_id, files in get_infos.items():
                    sort_dict = {}
                    model_file_list = []
                    model_info_file_list = []
                    for file in files['files']:
                        file_name, file_ext = file.split('.') # "lasso.txt"   
                        if file_ext == 'model':
                            model_file_list.append(file)        
                        elif file_ext == 'txt':
                            model_info_file_list.append(file)
                    sort_dict['model_files'] = model_file_list
                    sort_dict['model_infos'] = model_info_file_list
                    sort_final_dict[p_id] = sort_dict

                # get_infos = sorted(get_infos.items())
                result_['result'] = sort_final_dict
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
        # TODO 모델 생성 함수 정리
        data_path = request.data["data_path"]
        result = parking_model(data_path)
        result = True
        if result:
            return Response('Create model done', status=status.HTTP_200_OK)
        else:
            return Response('Create model fail', status=status.HTTP_400_BAD_REQUEST)


class BatchModelView(APIView):
    # 모델 배치 조회
    def get(self, request):
        batch_id = str(request.GET['batch_id'])
        print('batch_id', batch_id)

        # 모델 id의 배치 상태 확인 
        from django_apscheduler.models import DjangoJobExecution, DjangoJob
        if not batch_id in list(DjangoJob.objects.all().values_list("id", flat=True)):
            return Response(f'check batch_id : {batch_id} is not existed', 
                            status=status.HTTP_400_BAD_REQUEST)

        get_scheduler = AppConfig.dj_scheduler
        # list [<Job (id=1 name=oneM2M_update)>]
        print("get_jobs() : ", get_scheduler.get_jobs())
        for single_job in get_scheduler.get_jobs():
            if batch_id == str(single_job.id):
                return_dict = {}
                for attr in ['id', 'func_ref', 'args', 'name', 'next_run_time', 'trigger']:
                    if attr != 'trigger':
                        return_dict[attr]=getattr(single_job, str(attr))
                    else:
                        return_dict['trigger'] = str(single_job.trigger)
                        return_dict['timezone'] = str(single_job.trigger.timezone)
                return Response(return_dict, status=status.HTTP_200_OK)
            else:
                return Response('check batch_id', status=status.HTTP_400_BAD_REQUEST)

    # 모델 배치 실행(생성)
    def post(self, request):
        """
        index = "전체 주차면적 중 가능면적 비율(%)"
        predictedFor = "배치가 실행된 시점"
        """
        data_path = request.data["data_path"]
        model_name = request.data["model_name"]
        batch_id = request.data["batch_id"]
        is_success = model_patch_apscheduler(data_path, model_name, batch_id)
        if not is_success:
            return Response('fail to execute batch', 
                status=status.HTTP_400_BAD_REQUEST)

        return Response('execute batch', 
            status=status.HTTP_200_OK)
