# -*- coding: utf-8 -*-
import os, json
import pandas as pd
import joblib
from os_utils import path_join


def generate_train_data(data_set, p_id):
    data_set = data_set[data_set['id'] == p_id]
    y = data_set['availableSpotNumber'].values
    X = data_set.drop(['availableSpotNumber', 'totalSpotNumber', 'id'], axis=1)
    return X, y

# def generate_test_data(data_set, p_id):
#     data_set = data_set.drop(['date'], axis=1)
#     data_set = data_set[data_set['p_id'] == p_id]
#     X_id = data_set.id.tolist()
#     data_set = data_set.drop(["id"], axis=1)
#     X = [','.join(map(str, tup)).split(',') for tup in data_set.drop(['p_id'], axis=1).values]
#     return X, X_id

def save_estimator(estimator, path_):
    joblib.dump(estimator, path_)

def save_estimator_info(estimator, data, path_, filename_, score_=None, params_=None):
    filename = filename_ + '.txt'
    # cv_ = [0.8, 0.85, 0.83323]
    
    if type(estimator).__name__ == 'GridSearchCV':
        model_name = type(estimator.estimator).__name__
    else:
        model_name = type(estimator).__name__
    results = dict(model_name = model_name,
                   columns_name = data.columns.tolist(),
                   # best_score = [round(score, 2) for score in score_],
                   best_score = score_,
                   best_param = str(params_)
                  )

    with open(path_join([path_, filename]), 'w', encoding='utf-8') as f:
        f.write(json.dumps(results))


def load_estimator(estimator, case, p_id):
    path_ = os.path.join('model', estimator)
    model_list = os.listdir(path_)
    model = [m for m in model_list if ('case'+case in m) and (p_id in m)]
    if len(model) != 1:
        raise StopIteration("Error in value of case")
    path_ = os.path.join(path_, model[0])
    return joblib.load(path_), model[0]


def output(data_set, y_pred, estimator, model_name):
    path_ = os.path.join('result', estimator)
    with open(path_+'/'+model_name+'.txt', 'w') as f:
        f.write('#주차장ID\t날짜\t시간대\t주차가능변수\n')
        for y, (i, d) in zip(y_pred, data_set.iterrows()):
            p_id = d.p_id
            date = d.date
            time = d.time.split(',').index('1')
            f.write('\t'.join(map(str, [p_id, date, time, y]))+'\n')
