# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import pandas as pd

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__)) # ../parking/app
_UTILS_DIR = os.path.join(_SCRIPT_DIR, 'utils') # ../parking/app/utils
sys.path.insert(0, os.path.abspath(_UTILS_DIR))

from os_utils import path_join, create_dir
from data_helpers import generate_train_data, save_estimator, save_estimator_info, load_estimator
from feature_engineering import convert_datetime, data_standard_scaling, convert_binary_vector
from estimator_definition import get_estimator, get_grid_search


logger = logging.getLogger("collect_log")


def train_process(data_path, p_id):
    try:
        model_name = 'lgbm'
        train_set = pd.read_json(data_path)
        logger.info('Parking ID : {} '.format(p_id))
        logger.info('Shape of total train set : {}'.format(train_set.shape)) 
        
        # 모델 및 모델 정보 저장 경로 지정
        model_dir = path_join(['model', str(p_id)])
        create_dir(model_dir)

        # data preparation - X, y split
        X, y = generate_train_data(train_set, p_id)

        # 데이터 전처리 - NUMS / CATS
        NUM_COLS = ['temperature', 'windSpeed', 'humidity', 'hourlyRainfall']
        CAT_COLS = ['weatherType', 'isHoliday']

        # 변수 전처리
        X = convert_datetime(X)
        X = data_standard_scaling(X, NUM_COLS, model_dir, True)
        X = convert_binary_vector(X, CAT_COLS)

        # 요청한 학습데이터로 모델 새로 생성
        clf = get_estimator(model_name)
        grid_model = get_grid_search(clf , model_name)
        grid_model.fit(X, y)

        best_score = grid_model.best_score_
        best_param = grid_model.best_params_
        logger.info('Grid Search done. => Model : {}, Best Score : {:.4f}, Best Parameters : {}'\
            .format(p_id + '_' + model_name, best_score, best_param))
        
        save_estimator(grid_model, model_dir + "/" + model_name + '.model')
        save_estimator_info(estimator=grid_model,
                            data=X, 
                            path_=model_dir, 
                            filename_= model_name,
                            score_=best_score, 
                            params_=best_param)
        logger.info('Save the trained model done.')
        return True
    except Exception as e:
        logger.error(f'error msg:{e}')
        return False


def parking_model(data_path, parking_id):
    logger.info('Start Train!')
    if train_process(data_path, parking_id):
        logger.info('Finish Train!')
        logger.info('')
        return True
    else:
        return False



