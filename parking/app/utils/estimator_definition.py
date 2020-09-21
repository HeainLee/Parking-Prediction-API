from sklearn.model_selection import KFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso

PARAM_GRID = {
              'rfr':{'max_depth': [2, 4, 6], 'n_estimators': [10, 50, 100]},
              'ridge':{'alpha':[0.01, 0.1, 1, 2, 4, 10, 100, 200, 400]},
              'lasso':{'alpha':[0.02, 0.024, 0.025, 0.026, 0.03]}
}


def get_estimator(estimator):
    if estimator == 'ridge':
        clf = Ridge()
    elif estimator == 'rfr':
        clf = RandomForestRegressor()
    elif estimator == 'lasso':
        clf = Lasso()
    else:
        raise Exception("Name of esimator is error.")
    return clf


def get_grid_search(clf, estimator):
    return GridSearchCV(estimator=clf, param_grid=PARAM_GRID[estimator], cv=5)


def get_grid_search(clf, model):
    kfold = KFold(n_splits=2, shuffle=True, random_state=1)
    grid_model = GridSearchCV(estimator=clf, 
                              param_grid=PARAM_GRID[model],
                              # scoring='r2',
                              refit=True,
                              iid=True, 
                              cv=kfold,
                              # n_jobs = -1, 
    )
    return grid_model