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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ParkingModelView(APIView):
    # 주차장 모델 생성 결과 조회 
    def get(self, request):
        try:
            if request.GET.get('parking_id', False):
                p_id = request.GET['parking_id']
                filename = 'lgbm.txt'
                model_path = f'{BASE_DIR}/model'
                print(model_path)

                if filename.endswith('.txt'):
                    load_path = os.path.join(model_path, str(p_id), filename)
                    with open(load_path, 'r', encoding='UTF-8') as f:
                        get_info = json.loads(f.read())
                    model_info = dict(model_info=get_info)

                    final_result = {}
                    final_result['path'] = load_path
                    final_result['result'] = model_info
                    return Response(final_result, status=status.HTTP_200_OK)

                    
            else:
                query_key = ["dirname", "filename"]
                model_path = f'{BASE_DIR}/model'

                result_ = {}
                result_["path"] = str
                result_['result'] = []
                get_infos = {}
                for dirpath, dirnames, filenames in os.walk(model_path):
                    if dirpath == model_path:
                        result_['path'] = dirpath
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
                        file_name, file_ext = file.split('.') 
                        if file_ext == 'model':
                            model_file_list.append(file)        
                        elif file_ext == 'txt':
                            model_info_file_list.append(file)
                    sort_dict['model_files'] = model_file_list
                    sort_dict['model_infos'] = model_info_file_list
                    sort_final_dict[p_id] = sort_dict

                result_['result'] = sort_final_dict
                return Response(result_, status=status.HTTP_200_OK)

        except FileNotFoundError as e:
            error_return = {}
            error_return["error_type"] = 'FileNotFoundError'
            error_return["error_message"] = e.strerror
            return Response(error_return, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_return = {}
            error_return["error_type"] = e.__class__.__name__
            error_return["error_message"] = str(e)
            return Response(error_return, status=status.HTTP_400_BAD_REQUEST)

    # 주차장 모델 생성
    def post(self, request):
        # 모델 생성하고 결과 반환
        parking_id = request.data["parking_id"]
        data_path = request.data["data_path"]

        result = parking_model(data_path, parking_id)
        if result:
            return_value = dict(
                pakring_id=parking_id,
                train_data=data_path,
                model_saved_path=f'{BASE_DIR}/model/{parking_id}'

                )
            return Response(return_value, status=status.HTTP_200_OK)
        else:
            return_value = dict(
                error_type="400 Bad Request",
                error_message="Create model fail - check logfile",
                error_description=f"logfile path - {BASE_DIR}/logfile.log"
                
                )
            return Response(return_value,
                status=status.HTTP_400_BAD_REQUEST)


class BatchModelView(APIView):
    # 모델 배치 조회
    def get(self, request):
        batch_id = str(request.GET['parking_id'])

        # 모델 id의 배치 상태 확인 
        from django_apscheduler.models import DjangoJobExecution, DjangoJob
        is_id = batch_id in list(DjangoJob.objects.all().values_list("id", flat=True))
        if not is_id:
            return Response(f'check batch_id : {batch_id} is not existed', 
                            status=status.HTTP_400_BAD_REQUEST)

        get_scheduler = AppConfig.dj_scheduler

        try:
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
                    pass
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


    # 모델 배치 실행(생성)
    def post(self, request):
        """
        index = "전체 주차면적 중 가능면적 비율(%)"
        predictedFor = "배치가 실행된 시점"
        """
        parking_id = request.data["parking_id"]
        data_folder = request.data["data_folder"]
        batch_id = str(parking_id)

        # 로컬로 테스트 할 때 
        # is_success = parking_model_test(data_path, parking_id)

        # 실제 배치로 돌릴 때
        is_success, msg = model_patch_apscheduler(data_folder, parking_id, batch_id)
        if not is_success and msg == "":
            error_return = {}
            error_return["error_type"] = "HTTP_400_BAD_REQUEST"
            error_return["error_message"] = "fail to execute batch"
            return Response(error_return, 
                status=status.HTTP_400_BAD_REQUEST)
        elif not is_success and msg == "existing":
            error_return = {}
            error_return["error_type"] = "HTTP_409_CONFLICT"
            error_return["error_message"] = f"batch of model [{batch_id}] already exist"
            return Response(error_return,
                status=status.HTTP_409_CONFLICT)

        return Response(json.loads(msg), 
            status=status.HTTP_202_ACCEPTED)
