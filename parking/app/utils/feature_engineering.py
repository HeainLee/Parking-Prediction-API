import os, joblib
import datetime
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pandas.api.types import CategoricalDtype


WEEKS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
HOURS = [x for x in range(0, 24)]
MINTS = [x for x in range(0, 60)]

def data_standard_scaling(data_set, cols, base_path, is_train=True):
    for col in cols:
        if is_train:
            SCALER = StandardScaler()
            scaled_data = SCALER.fit_transform(data_set[col].values.reshape(-1, 1))
            file_name = 'scaler_' + str(col) + '.pickle'
            file_path = os.path.join(base_path, file_name)
            joblib.dump(SCALER, file_path) 
        else:
            file_name = 'scaler_' + str(col) + '.pickle'
            file_path = os.path.join(base_path, file_name)
            loaded_SCALER = joblib.load(file_path)
            scaled_data = loaded_SCALER.transform(data_set[col].values.reshape(-1, 1))
        
        data_set[col] = scaled_data

    return data_set


def convert_binary_vector(data_set, cols):

    def _one_hot_encoding(data_set, col):
        df_convert = pd.concat([data_set,
            pd.get_dummies(data_set[str(col)], prefix=str(col))], 
            axis=1
            )
        df_convert.drop([str(col)],axis=1, inplace=True)
        return df_convert

    # for col in cols:       
        # data_set = _one_hot_encoding(data_set, col)
    isHoliday_CAT = [True, False]
    weatherType_CAT = ['맑음', '비', '비/눈', '눈']

    data_set['isHoliday'] = data_set.isHoliday.astype(pd.CategoricalDtype(categories=isHoliday_CAT))
    data_set['weatherType'] = data_set.weatherType.astype(pd.CategoricalDtype(categories=weatherType_CAT))

    data_set = pd.concat([data_set, pd.get_dummies(data_set["isHoliday"], prefix='isHoliday')], axis=1)
    data_set = pd.concat([data_set, pd.get_dummies(data_set["weatherType"], prefix='weatherType')], axis=1)
    data_set.drop([str('weatherType'), str('isHoliday')],axis=1, inplace=True)
    return data_set


def convert_datetime(data_set):
    # datetime 컬럼을 요일/시간으로 변환
    try:
        data_set['weekday'] = data_set.dateTime.apply(lambda \
            x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date().strftime('%A'))
        data_set['hour'] = data_set.dateTime.apply(lambda \
            x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").hour)
        date_set['minu'] = data_set.dateTime.apply(lambda \
            x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").minute)
    except:
        data_set['weekday'] = data_set.dateTime.apply(lambda x: x.date().strftime('%A'))
        data_set['hour'] = data_set.dateTime.apply(lambda x: x.hour)
        data_set['minu'] = data_set.dateTime.apply(lambda x: x.minute)


    data_set.drop([str('dateTime')], axis=1, inplace=True)
    
    # 요일을 원핫인코딩 변환
    try:
        cat_type = CategoricalDtype(categories=WEEKS, ordered=True)
        data_set['weekday'] = data_set['weekday'].astype(cat_type)
    except:
        data_set["weekday"] = data_set.weekday.astype('category', categories=WEEKS)
    data_set = pd.concat([data_set, 
        pd.get_dummies(data_set["weekday"], prefix='weekday')], 
        axis=1
        )
    data_set.drop([str('weekday')], axis=1, inplace=True)


    # 시간을 원핫인코딩으로 변환
    try:
        cat_type = CategoricalDtype(categories=HOURS, ordered=True)
        data_set['hour'] = data_set['hour'].astype(cat_type)
    except:
        data_set["hour"] = data_set.hour.astype('hour', categories=HOURS)
    data_set = pd.concat([data_set, 
        pd.get_dummies(data_set["hour"], prefix='hour')],
        axis=1
        )
    data_set.drop([str('hour')], axis=1, inplace=True)

    # 분 단위 변환 & 원핫인코딩
    bins = [x for x in range(0,60,5)]
    minu_CAT = [str(x)+"-"+str(x+5) for x in range(0,60,5)]

    data_set['minu'] = np.vectorize(
        dict(enumerate(minu_CAT, 1)).get)(np.digitize(data_set['minu'],bins))
    data_set['minu'] = data_set.minu.astype(pd.CategoricalDtype(categories=minu_CAT))
    data_set = pd.concat([data_set, pd.get_dummies(data_set["minu"], prefix='minu')], axis=1)

    data_set.drop([str('minu')], axis=1, inplace=True)


    return data_set

