from sklearn.model_selection import KFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso
from lightgbm.sklearn import LGBMRegressor
from scipy.stats import randint as sp_randint
from scipy.stats import uniform as sp_uniform


PARAM_GRID = {
              'rfr':{'max_depth': [2, 4, 6], 'n_estimators': [10, 50, 100]},
              'ridge':{'alpha':[0.01, 0.1, 1, 2, 4, 10, 100, 200, 400]},
              'lasso':{'alpha':[0.02, 0.024, 0.025, 0.026, 0.03]},
              'lgbm':{'learning_rate': [0.01, 0.1, 1], 'n_estimators': [20, 40]}
             }

def get_estimator(estimator):
    if estimator == 'ridge':
        clf = Ridge()
    elif estimator == 'rfr':
        clf = RandomForestRegressor()
    elif estimator == 'lasso':
        clf = Lasso()
    elif estimator == 'lgbm':
        clf = LGBMRegressor()
    else:
        raise Exception("Name of esimator is error.")
    return clf

def get_grid_search(clf, model):
    kfold = KFold(n_splits=2, shuffle=True, random_state=1)
    grid_model = GridSearchCV(estimator=clf, 
                              param_grid=PARAM_GRID[model],
                              refit=True,
                              iid=True, 
                              cv=kfold,
                              verbose=1,
                              n_jobs=-1
    )
    return grid_model
