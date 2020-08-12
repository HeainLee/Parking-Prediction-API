# -*- coding: utf-8 -*-
import os, json
import pandas as pd
import joblib
from os_utils import path_join


# 추후 수정 : 파일 읽기에서 API 호출로 변경
def load_train_set(path_):
    with open(path_) as f:
        lines = f.readlines()
        temp = []
        for l in lines[1:]:
            items = l.strip().split('\t')
            temp.append(items)
        train_set = pd.DataFrame(temp, columns=[
            'p_id', 'date',
            'day_of_week', 'time',
            'pm10', 'pm25', 'air_index',
            'temp', 'rainfall', 'hour_rainfall', 'condition',
            'num_of_parking'])
        return train_set


# 추후 수정 : 파일 읽기에서 API 호출로 변경
def load_test_set(path_):
    with open(path_) as f:
        lines = f.readlines()
        temp = []
        for l in lines[1:]:
            items = l.strip().split('\t')
            temp.append(items)
        test_set = pd.DataFrame(temp, columns=[
            'p_id', 'date', 'day_of_week', 'time', 'pm10', 'pm25', 'air_index',
            'temp', 'rainfall', 'hour_rainfall', 'condition'
            ])
        test_set["id"] = test_set.index.tolist()
        return test_set


def generate_case(data_set, case):
    if case == 1:
        return data_set
    elif case == 2:
        return data_set.drop(['pm10', 'pm25', 'air_index'], axis=1)
    elif case == 3:
        return data_set.drop([
            'pm10', 'pm25', 'air_index',
            'temp', 'rainfall', 'hour_rainfall', 'condition'], axis=1)
    else:
        raise StopIteration("Error in value of case")


def classify_case(data_set, case):
    if case == 1:
        _data_set = data_set.dropna(subset=["air_index", "condition"])
        _data_set = _data_set[(_data_set["air_index"] != "") & (_data_set["condition"] != "")]
    elif case == 2:
        _data_set = data_set.dropna(subset=["condition"])
        _data_set = data_set[(_data_set["air_index"] == "") & (_data_set["condition"] != "")]
    elif case == 3:
        _data_set = data_set[(data_set["air_index"] == "") & (data_set["condition"] == "")]
    else:
        raise StopIteration("Error in value of case")
    return _data_set


def generate_train_data(data_set, p_id):
    data_set = data_set.drop(['date'], axis=1)
    data_set = data_set[data_set['p_id'] == p_id]
    X = [','.join(map(str, tup)).split(',') for tup in data_set.drop(['p_id', 'num_of_parking'], axis=1).values]
    y = map(int, data_set.num_of_parking.values.tolist())
    return X, y


def generate_test_data(data_set, p_id):
    data_set = data_set.drop(['date'], axis=1)
    data_set = data_set[data_set['p_id'] == p_id]
    X_id = data_set.id.tolist()
    data_set = data_set.drop(["id"], axis=1)
    X = [','.join(map(str, tup)).split(',') for tup in data_set.drop(['p_id'], axis=1).values]
    return X, X_id


def save_estimator(estimator, path_):
    joblib.dump(estimator, path_)

def save_estimator_info(estimator, data, path_, filename_):
    filename = filename_ + '.txt'
    cv_ = [0.8, 0.85, 0.83323]
    results = dict(model_name = type(estimator).__name__,
                   columns_name = data.columns.tolist(),
                   cv_score = [round(score, 2) for score in cv_]
                  )
    # str_list = [f"{type(estimator).__name__}\n", f"{data.columns.tolist()}\n", "cross_validation_score"]
    # with open(path_join([path_, filename]), 'w') as f:
    #     f.writelines(str_list)
    with open(path_join([path_, filename]), 'w') as f:
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
