import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_squared_log_error

# origin = np.array([1, 2, 3, 2, 3, 5, 4, 6, 5, 6, 7])
# pred = np.array([1, 1, 2, 2, 3, 4, 4, 5, 5, 7, 7])


def reg_metrics(origin, pred, n=0, p=0):
    MAE =  mean_absolute_error(origin, pred)
    # 실제 값과 예측 값의 차이를 절댓값으로 변환해 평균한 것
    # MAE = 0.45454545454545453

    MSE = mean_squared_error(origin, pred)
    # 실제 값과 예측 값의 차이를 제곱해 평균한 것
    # MSE = 0.45454545454545453

    RMSE = np.sqrt(MSE)
    # MSE 값은 오류의 제곱을 구하므로 실제 오류 평균보다 더 커지는 특성이 있어 MSE에 루트를 씌운 RMSE 값을 쓰는 것
    # RMSE = 0.674199862463242

    MSLE = mean_squared_log_error(origin, pred)
    # MSE에 로그를 적용해준 지표입니다. log(y)가 아니라 log(y+1)
    # MSLE = 0.029272467607503516

    RMSLE = np.sqrt(mean_squared_log_error(origin, pred))
    # RMSE에 로그를 적용해준 지표입니다.
    # RMSLE = 0.1710919858073531

    R2 = r2_score(origin, pred)
    # R² 는 분산 기반으로 예측 성능을 평가
    # R2 = 0.868421052631579

    ADJ_R2 = 1 - (1-R2)*(n-1)/(n-p-1)

    print(dict(mae=MAE, mse=MSE, rmse=RMSE, msle=MSLE, rmsle=RMSLE, r2=R2, adj_r2=ADJ_R2))

    # return dict(mae=MAE, mse=MSE, rmse=RMSE, msle=MSLE, rmsle=RMSLE, r2=R2)