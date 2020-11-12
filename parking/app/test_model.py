# -*- coding: utf-8 -*-
import os
import sys
import json
import argparse
import logging
import pandas as pd
from datetime import datetime
from pandas.io.json import json_normalize

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__)) # ../parking/app
_UTILS_DIR = os.path.join(_SCRIPT_DIR, 'utils') # ../parking/app/utils
sys.path.insert(0, os.path.abspath(_UTILS_DIR))

from os_utils import path_join, create_dir
from data_helpers import generate_test_data, load_estimator
from feature_engineering import convert_datetime, data_standard_scaling, convert_binary_vector
from estimator_definition import get_estimator, get_grid_search


logger = logging.getLogger("collect_log")
batch_logger = logging.getLogger("collect_log_batch")


def test_process(data_folder, p_id):
    try:
        # 현재시간으로 테스트 데이터 불러오기
        logger.info(f"current_time: {datetime.now()}")
        now = datetime.now()
        year = '{:02d}'.format(now.year)
        month = '{:02d}'.format(now.month)
        day = '{:02d}'.format(now.day)

        # 10시 기준 최신데이터 : 9시 데이터
        data_name = '/' + str(year+month+day) + '_' + str(int(now.hour) - 1)+'.json'
        model_name = 'lgbm'
        data_path = os.path.join(data_folder + data_name)

        try:
            with open(data_path) as data_file:    
                test_set = json_normalize(json.load(data_file),sep='_')
        except Exception as e:
            test_set = pd.read_csv(data_path)
            test_set['dateTime'] = pd.to_datetime(test_set['dateTime'],
                format='%Y-%m-%d %H:%M:%S', errors='raise')

        logger.info('Parking ID : {} '.format(p_id))
  
        # 저장된 모델 경로
        model_dir = path_join(['model', str(p_id)])
        
        # 테스트용 데이터 생성(hour별 12row - observation 결합)
        X, total_spot_num = generate_test_data(test_set, p_id)

        # 테스트 X columns
        temp_time = X['dateTime']
        logger.info(f"테스트 데이터 시간대: {temp_time[0]}")

        # 데이터 전처리 - NUMS / CATS
        NUM_COLS = ['temperature', 'windSpeed', 'humidity', 'hourlyRainfall']
        CAT_COLS = ['weatherType', 'isHoliday']
        # EXC_COLS = ['availableSpotNumber', 'totalSpotNumber']

        # 숫자형 변수를 전처리
        X = convert_datetime(X)
        X = data_standard_scaling(X, NUM_COLS, model_dir, False)
        X = convert_binary_vector(X, CAT_COLS) 

        # 모델 다운로드 / 주차면적 예측 / 예측결과 변환
        clf = load_estimator(model_name, p_id)
        logger.info('Load the Model [{}] for {} done.'.format(model_name, p_id))
        logger.info('모델 베스트 스코어 {}'.format(clf.best_score_))
        y_pred = [int(i) for i in clf.predict(X)]


        logger.info('{} 면적의 총 주차장 면적 {}'.format(p_id, total_spot_num))
        logger.info('{} 면적의 {} 시 주차가능 비율 (%)'.format(p_id, temp_time[0].hour))
        pred_list = [int(i) for i in list(map(lambda x: (x/total_spot_num)*100, y_pred))]
        logger.info([round(elem, 2) for elem in pred_list])

        batch_log = {
        "current_time": str(datetime.now().strftime("%Y-%m-%dT%H:%M:%S")),
        "parking_id": str(p_id),
        "test_data": data_name,
        "dateTime": temp_time.dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        "predict_cnt": list(y_pred), 
        "predict_perc": pred_list
        }
        batch_log = json.dumps(batch_log)

        # 배치 결과 파일로 저장 "batch_log.json"
        batch_logger.info(batch_log)


        predictedFor_list = temp_time.dt.strftime('%Y%m%dT%H%M%S').tolist()

        update_data = []
        for i in range(len(pred_list)):
            index_dict = {}
            index_dict["index"] = pred_list[i]
            index_dict["predictedFor"] = predictedFor_list[i]
            update_data.append(index_dict)

        logger.info('Success to get Congestion Prediction of {}.'.format(p_id))

        return True, update_data
    except Exception as e:
        logger.error('error!')
        logger.error(e)
        return False, []


def parking_model_test(data_path, parking_id):
    logger.info('Start!')
    is_success, update_data = test_process(data_path, parking_id)
    if is_success:
        logger.info('Finish!')
        logger.info('')
        return True, update_data
    else:
        return False, []


def oneM2M_update(data_folder, parking_id):
    import requests
    import json
    # 모델의 예측 결과(주차가능면적) 생성
    result, update_data = test_process(data_folder, parking_id)
    if result:
        print('결과생성 성공!')
    else:
        print('결과생성 실패!')

    # oneM2M platform and API settings
    url_keti = f'http://203.253.128.179:7599/wdc_base/sync_parking/parkingLot_KETI/congestion_{parking_id}'
    headers = {'Content-Type': 'application/json', 'X-M2M-Origin': 'SM', 'X-M2M-RI': '1234'}

    # data 
    congestionPrediction = update_data

    data = {
        'sc:parkingBlock': {
            'congestionPrediction': congestionPrediction}
    }

    resp = requests.put(url_keti, headers=headers, data=json.dumps(data))
    logger.info('Save the result of model prediction done.')
    if resp.status_code == 200:
        return True
    else:
        return False


def model_patch_apscheduler(data_folder, parking_id, batch_id):
    cron_time = {
                "KETI_Block_A": '0',
                "KETI_Block_B": '1',
                "KETI_Block_C": '2',
                "KETI_Block_D": '3',
                "KETI_Block_E": '4',
                "KETI_Block_F": '5',
                "KETI_Block_G": '6',
                "KETI_Block_H": '7',
                "KETI_Block_Visitor": '8',
    }
    try:
        from .apps import AppConfig
        get_scheduler = AppConfig.dj_scheduler

        if get_scheduler.get_job(batch_id) != None:
            if get_scheduler.get_job(batch_id).id == batch_id:
                return False, "existing"

        else:
            get_scheduler.add_job(oneM2M_update,
                                  'cron',
                                  minute=cron_time[parking_id],
                                  hour='*/1',
                                  max_instances=1,
                                  id=str(batch_id),
                                  args=[data_folder, parking_id]
                                  )
            batch_info = {
            "batch_id":batch_id, 
            "next_run_time": get_scheduler.get_job(batch_id).next_run_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return True, json.dumps(batch_info)
    except Exception as e:
        print(e)
        return False, ""

