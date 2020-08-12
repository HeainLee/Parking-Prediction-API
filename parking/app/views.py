from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
from .train_model import parking_model
import os, json
from datetime import datetime

class ParkingModelView(APIView):
    # 주차장 모델 생설 결과 조회 
    def get(self, request):
        try:
            query_key = ["dirname", "filename"]
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
        result = parking_model()
        if result:
            return Response('모델이 생성되었습니다.', status=status.HTTP_200_OK)
        else:
            return Response('모델 생성 실패했습니다.', status=status.HTTP_400_BAD_REQUEST)


class ParkingModelDetailView(APIView):
    def get(self, request, pk):
        if request.GET:
            print('모델 배치')
            batch_req = request.GET["batch"]
            if batch_req == "start":
                return Response('배치 시작')
            elif batch_req == "status":
                return Response('배치 상태 확인')

                
            # elif batch_req == "stop" # or "revise"

            else:
                return Response('배치 작업을 지정해서 요청해주세요.')
        else:
            print('모델 조회')
            model_path = "/Users/heain/parking_prediction_api/parking/model"
            model_dir = [i for i in os.listdir(model_path) if not '.' in i ]
            model_dir.sort()
            print(model_dir)
            if pk in model_dir:
                def _case_get_info(path):
                    mtime = _convert_date(os.path.getmtime(path))
                    ctime = _convert_date(os.path.getctime(path))
                    stsize = os.path.getsize(path)
                    return mtime, ctime, stsize

                def _convert_date(timestamp):
                    date_obj = datetime.fromtimestamp(timestamp)
                    return date_obj

                model_path = model_path + "/" + str(pk)
                files = os.listdir(model_path)
                # ['parkingLot_2.model', 'parkingLot_1.model']
                model_files = [file for file in files if '.model' in file]
                # ['parkingLot_1.txt', 'parkingLot_2.txt']
                model_infos = [file for file in files if '.txt' in file]
                print(model_files, model_infos)
                # mtime, ctime, stsize = _case_get_info(model_path)

                return_info = []
                for model in model_files:
                    model_info = {}
                    model_name = model.split('.model')[0]
                    print(model_name) # parkingLot_2
                    for info in model_infos:
                        print(info)
                        if model_name in info:
                            load_path = os.path.join(model_path,info)
                            with open(load_path, 'r', encoding='UTF-8') as f:
                                get_info=json.loads(f.read())


                    model_info['model_name'] = model
                    model_info['model_info'] = get_info
                    return_info.append(model_info)

                final_result = {}
                final_result['path'] = model_path
                final_result['result'] = return_info
                # file_info={}
                # file_info["createdAt"] = mtime
                # file_info["modifiedAt"] = ctime
                # file_info["filesize"] = stsize
                return Response(final_result, status=status.HTTP_200_OK)

            else:
                error_return = dict(error=404, 
                                    message=f"Model '{pk}' Not Found")
                return Response(error_return, 
                    status=status.HTTP_404_NOT_FOUND)

