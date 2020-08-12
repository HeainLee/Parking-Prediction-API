# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
_UTILS_DIR = os.path.join(_SCRIPT_DIR, 'utils')
sys.path.insert(0, os.path.abspath(_UTILS_DIR))

from os_utils import path_join, create_dir, next_path
from data_helpers import load_train_set, generate_case, generate_train_data, save_estimator, save_estimator_info
from feature_engineering import convert_binary_vector, train_standard_scaling
from estimator_definition import get_estimator, get_grid_search
from metrics import rmse


def get_args():
    parser = argparse.ArgumentParser(description='Parking Congestion Prediction')
    parser.add_argument('-e', '--estimator', nargs='?', choices=['svr', 'rfr'],
                        help='Choose an estimator for training.', required=True)
    args = parser.parse_args()
    estimator = args.estimator
    return estimator


def _load_data():
    train_set = load_train_set(path_=_SCRIPT_DIR+'/data/train_data.txt')
    train_set = convert_binary_vector(train_set)
    train_set = train_standard_scaling(train_set)
    return train_set


def _print_train_info(data_set):
    columns_ = data_set.columns.values
    logging.debug(data_set.head())
    logging.debug('X : {}'.format(columns_[1:-1]))
    logging.debug('y : {}'.format(columns_[-1]))


def train_process():
    # estimator = get_args()

    # 모델 저장 디렉토리 생성
    # model_dir = path_join(['model', estimator])
    next_num = next_path('model')
    model_dir = path_join(['model', str(next_num)])
    print(model_dir)
    create_dir(model_dir)

    # 학습용 데이터 로드 및 기본 전처리
    train_set = _load_data()
    logging.debug('Shape of total train set : {}'.format(train_set.shape))

    from sklearn.ensemble import RandomForestRegressor
    clf = RandomForestRegressor()
    
    p_id = 'parkingLot_1'
    save_estimator(clf, model_dir + '/' + str(p_id) + '.model')
    save_estimator_info(clf, train_set, model_dir, p_id)
    logging.debug('Save the trained model done.')

    return True

    # 모델 학습 
    train = dict()
    for case in range(1, 4):
        logging.debug('Case {}'.format(case))

        train[case] = generate_case(train_set, case)
        _print_train_info(train[case])
        logging.debug('Shape of feature : {}'.format(train[case].shape))

        p_ids = train[case].p_id.unique()
        for p_id in p_ids:
            logging.debug('p_id : {}'.format(p_id))

            X, y = generate_train_data(train[case], p_id)
            logging.debug('# of train data : {}'.format(len(X)))

            clf = get_estimator(estimator)
            clf = get_grid_search(clf, estimator)
            clf.fit(X, y)
            logging.debug('Grid Search done.\nBest Score : {:.4f}, Best Parameters : {}'.format(
                clf.best_score_, clf.best_params_))

            y_pred = clf.predict(X)
            logging.debug('RMSE : {:.4f}'.format(rmse(y, y_pred)))

            save_estimator(clf, model_dir + '/case' + str(case) + '_' + str(p_id) + '.model')
            logging.debug('Save the trained model done.')

    logging.debug('Finish!')


def parking_model():
    print(_SCRIPT_DIR) # /Users/heain/parking_prediction_api/parking/app

    print(_UTILS_DIR) # /Users/heain/parking_prediction_api/parking/app/utils
    logging.basicConfig(format='%(asctime)s %(levelname)s (%(filename)s %(lineno)d) ::: %(message)s',
                        level=logging.DEBUG)
    if train_process():
        return 'train_process'
    else:
        return 'wrong'



