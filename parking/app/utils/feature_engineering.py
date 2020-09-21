import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pandas.api.types import CategoricalDtype


WEEKS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
HOURS = [x for x in range(1, 25)]


def data_standard_scaling(data_set, cols):
    SCALER = StandardScaler()
    scaled_data = SCALER.fit_transform(data_set[cols].astype(float))
    data_set[cols] = scaled_data
    return data_set


def convert_binary_vector(data_set, cols):

    def _one_hot_encoding(data_set, col):
        df_convert = pd.concat([data_set,
            pd.get_dummies(data_set[str(col)], prefix=str(col))], 
            axis=1
            )
        df_convert.drop([str(col)],axis=1, inplace=True)
        return df_convert

    for col in cols:       
        data_set = _one_hot_encoding(data_set, col)        
    return data_set


def convert_datetime(data_set):
    # datetime 컬럼을 요일/시간으로 변환
    try:
        data_set['weekday'] = data_set.dateTime.apply(lambda \
            x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date().strftime('%A'))
        data_set['hour'] = data_set.dateTime.apply(lambda \
            x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").hour)
    except:
        data_set['weekday'] = data_set.dateTime.apply(lambda x: x.date().strftime('%A'))
        data_set['hour'] = data_set.dateTime.apply(lambda x: x.hour)

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
        data_set["hour"] = data_set.hour.astype('hour', categories=WEEKS)
    data_set = pd.concat([data_set, 
        pd.get_dummies(data_set["hour"], prefix='hour')], 
        axis=1
        )
    data_set.drop([str('hour')], axis=1, inplace=True)

    return data_set

