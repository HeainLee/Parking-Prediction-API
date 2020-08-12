from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV

'''
PARAM_GRID = {'svr': {'kernel': ['linear', 'rbf', 'poly'], 'gamma': [1e0, 1e1, 1e2], 'C': [1e0, 1e1, 1e2]},
              'rfr': {'max_depth': [2, 4, 6], 'n_estimators': [50, 100]}}
'''
PARAM_GRID = {'svr': {'kernel': ['linear'], 'gamma': [1e0], 'C': [1e0]},
              'rfr': {'max_depth': [2], 'n_estimators': [50]}}


def get_estimator(estimator):
    if estimator == 'svr':
        clf = SVR()
    elif estimator == 'rfr':
        clf = RandomForestRegressor()
    else:
        raise Exception("Name of esimator is error.")
    return clf


def get_grid_search(clf, estimator):
    return GridSearchCV(estimator=clf, param_grid=PARAM_GRID[estimator], cv=5)
