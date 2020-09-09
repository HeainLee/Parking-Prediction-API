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
from data_helpers import generate_train_data, save_estimator, save_estimator_info
from feature_engineering import convert_datetime, data_standard_scaling, convert_binary_vector
from estimator_definition import get_estimator, get_grid_search


logger = logging.getLogger("collect_log")


def _print_train_info(data_set):
    columns_ = data_set.columns.values
    logger.debug(data_set.head())
    logger.debug('X : {}'.format(columns_[1:-1]))
    logger.debug('y : {}'.format(columns_[-1]))


def train_process():
    # 학습용 데이터 로드
    
    # TODO : data_path 수정
    data_path = '/Users/heain/parking_prediction_api/train_data.json'
    train_set = pd.read_json(data_path)
    logger.info('Shape of total train set : {}'.format(train_set.shape))

    # 데이터 전처리 - NUMS / CATS
    NUM_COLS = ['temperature', 'windSpeed', 'humidity', 'hourlyRainfall']
    CAT_COLS = ['weatherType', 'isHoliday']
    # EXC_COLS = ['availableSpotNumber', 'totalSpotNumber']

    # 숫자형 변수를 전처리
    train_set = convert_datetime(train_set)
    train_set = data_standard_scaling(train_set, NUM_COLS)
    train_set = convert_binary_vector(train_set, CAT_COLS)   

    # 데이터 pid로 나누기 - id 의 유일한 값
    for p_id in train_set.id.unique():
        logger.info('Parking ID : {} '.format(p_id))
        
        # X, y split
        X, y = generate_train_data(train_set, p_id)

        # 회귀 모델 (선택 or 고정) - 그리디 서치 허용
        model_list = ['rfr', 'ridge', 'lasso']
        i = 0
        for model in model_list:
            i += 1
            logger.info('running ... {}/{}'.format(i, len(model_list)))
            clf = get_estimator(model)
            grid_model = get_grid_search(clf , model)
            grid_model.fit(X, y)
            best_score = grid_model.best_score_
            best_param = grid_model.best_params_
            logger.info('Grid Search done. => Model : {}, Best Score : {:.4f}, Best Parameters : {}'\
                .format(p_id + '_' + model, best_score, best_param))

            # 모델 및 모델 정보 저장
            model_dir = path_join(['model', str(p_id)]) # model/p_id/
            create_dir(model_dir)
            print('model_dir:',model_dir)
            save_estimator(grid_model, model_dir + "/" + model + '.model')
            save_estimator_info(estimator=grid_model, 
                                data=train_set, 
                                path_=model_dir, 
                                filename_= model,
                                score_=best_score, 
                                params_=best_param)
            logger.info('Save the trained model done.')

    logger.info('Finish!')
    return True


def parking_model():
    logger.info('Start!')
    print(_SCRIPT_DIR)
    print(_UTILS_DIR)
    if train_process():
        return True
    else:
        return False



