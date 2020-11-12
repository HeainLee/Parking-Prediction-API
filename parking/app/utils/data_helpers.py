# -*- coding: utf-8 -*-
import os, json
import pandas as pd
import joblib
from os_utils import path_join
from datetime import datetime

def generate_train_data(data_set, p_id):
    data_set = data_set[data_set['id'] == p_id]
    y = data_set['availableSpotNumber'].values
    X = data_set.drop(['availableSpotNumber', 'totalSpotNumber', 'id'], axis=1)
    return X, y


def generate_test_data(data_set, p_id):
    get_date = data_set['dateTime'].iloc[0]
    get_obser = data_set.drop(['prediction', 'dateTime', 'availableSpotNumber'], axis=1)

    # observation 가져오기
    get_obser = get_obser.drop_duplicates()

    if get_obser.shape[0] != 1:
        get_obser = get_obser[:1]

    get_obser=get_obser.append([get_obser]*11, ignore_index=True)

    # dateTime 생성하기
    datetime_list = []
    get_date = datetime.strptime(get_date, "%Y%m%dT%H%M%S")
    for n in range(0,60,5):
        year = '{:02d}'.format(get_date.year)
        month = '{:02d}'.format(get_date.month)
        day = '{:02d}'.format(get_date.day)
        hour = '{:02d}'.format(get_date.hour)
        hour = str(int(hour)+1) # 9 -> 10
        mins = '{:02d}'.format(n)
        secs = '00'
        day_month_year = '{}-{}-{}'.format(year, month, day)
        hour_mins_secs = '{}:{}:{}'.format(hour, mins, secs)
        datetime_list.append(day_month_year+'T'+hour_mins_secs)

    custom_df = pd.DataFrame({"dateTime":datetime_list})
    
    # observation + dateTime
    final_df = pd.concat([custom_df, get_obser], axis=1)
    final_df.rename(columns = {'observation_temperature' : 'temperature',
                               'observation_hourlyRainfall': 'hourlyRainfall',
                               'observation_windSpeed':'windSpeed',
                               'observation_weatherType':'weatherType',
                               'observation_humidity':'humidity'                          
                              }, inplace = True)

    final_df.dateTime = final_df.dateTime.apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S"))

    final_df = final_df[final_df['id'] == p_id]
    total_spot_num = final_df['totalSpotNumber']
    X = final_df.drop(['totalSpotNumber', 'id'], axis=1)    

    return X, total_spot_num.values[0]

def save_estimator(estimator, path_):
    joblib.dump(estimator, path_)


def save_estimator_info(estimator, data, path_, filename_, score_=None, params_=None):
    filename = filename_ + '.txt'
    
    if type(estimator).__name__ == 'GridSearchCV':
        model_name = type(estimator.estimator).__name__
    else:
        model_name = type(estimator).__name__
    results = dict(model_name = model_name,
                   data_nums = data.shape[0],
                   columns_name = data.columns.tolist(),
                   best_score = score_,
                   best_param = str(params_)
                  )

    with open(path_join([path_, filename]), 'w', encoding='utf-8') as f:
        f.write(json.dumps(results))


def load_estimator(estimator, p_id):
    path_ = os.path.join('model', str(p_id))
    model_list = os.listdir(path_)
    model = [m for m in model_list if '.model' in m and estimator in m]
    if len(model) != 1:
        raise StopIteration("Error in value of model")
    path_ = os.path.join(path_, model[0])
    return joblib.load(path_)

