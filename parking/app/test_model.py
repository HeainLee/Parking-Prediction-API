# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import pandas as pd

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__)) # /Users/heain/parking_prediction_api/parking/app
_UTILS_DIR = os.path.join(_SCRIPT_DIR, 'utils') # /Users/heain/parking_prediction_api/parking/app/utils
sys.path.insert(0, os.path.abspath(_UTILS_DIR))

from os_utils import path_join, create_dir
from data_helpers import generate_test_data, load_estimator
from feature_engineering import convert_datetime, data_standard_scaling, convert_binary_vector
from estimator_definition import get_estimator, get_grid_search


logger = logging.getLogger("collect_log")


def _print_train_info(data_set):
    columns_ = data_set.columns.values
    logger.debug(data_set.head())
    logger.debug('X : {}'.format(columns_[1:-1]))
    logger.debug('y : {}'.format(columns_[-1]))


def test_process(data_path, model_name):
    try:    
        # data_path = '/Users/heain/parking_prediction_api/test_data.json'
        test_set = pd.read_json(data_path)
        logger.info('Shape of total test set : {}'.format(test_set.shape))

        # 데이터 전처리 - NUMS / CATS
        NUM_COLS = ['temperature', 'windSpeed', 'humidity', 'hourlyRainfall']
        CAT_COLS = ['weatherType', 'isHoliday']
        # EXC_COLS = ['availableSpotNumber', 'totalSpotNumber']

        # 숫자형 변수를 전처리
        test_set = convert_datetime(test_set)
        test_set = data_standard_scaling(test_set, NUM_COLS)
        test_set = convert_binary_vector(test_set, CAT_COLS)   

        # 데이터 pid로 나누기 - id 의 유일한 값
        for p_id in test_set.id.unique():
            logger.info('Parking ID : {} '.format(p_id))
            
            # 테스트 X columns
            X, total_spot_num = generate_test_data(test_set, p_id)

            # 회귀 모델 (선택 or 고정) - 그리디 서치 허용
            clf = load_estimator(model_name, p_id)
            logger.info('Load the Model [{}] for {} done.'.format(model_name, p_id))
            logger.info('모델 베스트 스코어 {}'.format(clf.best_score_))
            y_pred = clf.predict(X)
            logger.info('모델 예측 주차장 면적 {}'.format(y_pred))
            logger.info('{} 면적의 총 주차장 면적 {}'.format(p_id, total_spot_num))
            # logger.info(list(map(lambda x: (x/total_spot_num)*100, y_pred)))
            pred_list = list(map(lambda x: (x/total_spot_num)*100, y_pred))
            logger.info('{} 면적의 주차가능 비율 (%)'.format(p_id))
            logger.info([round(elem, 2) for elem in pred_list])

            logger.info('Save the result of model prediction done.')
        return True
    except Exception as e:
        logger.error('error!')
        logger.error(e)
        return e


def parking_model_test(data_path, model_name):
    logger.info('Start!')
    print(_SCRIPT_DIR)
    print(_UTILS_DIR)
    if test_process(data_path, model_name):
        logger.info('Finish!')
        logger.info('')
        return True
    else:
        logger.error(test_process(data_path))
        return False


