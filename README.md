# Parking Prediction API

## Introduction
This repository was developed as Parking Congestion Prediction API with Django REST framework.

## Requirements 

- Software dependencies

```
python >= 3.6
```

## Installation

Install required python packages.

```
python3.6 -m pip install -r requirements.txt --upgrade
```

## To run

To run execute following steps:

#### Train step

```bash
curl -d '{"parking_id": "parking_id",
          "data_path":"home/path/data/parking_id/train_data.json}' \
     -H "Content-Type: application/json" \
     -X POST http://[host ip]:8000/parking/model
```

#### Batch(Test) step

```bash
curl -d '{"parking_id": "parking_id",
          "data_folder":"home/path/data/parking_id}'\
     -H "Content-Type: application/json" \
     -X POST http://[host ip]:8000/parking/batch
```

## Additional notes



1.  **API 목록**

1-1.  **API list**

| **기능구분**	| **HTTP 메서드**| **URI**    		  | **출력포맷**  | **설명**              | **파라미터**                            |
|----------|--------------|------------------|-------------|---------------------|---------------------------------------|
| 모델 관리   | POST			     | /parking/model   | json        | 모델 생성             |pakring_id=[주차ID], data_path=[데이터경로]                    |
|           | GET 			   | /parking/model   | json        | 학습된 모델 조회        |                                       |
|           | GET 			   | /parking/model   | json        | 학습된 모델 상세 조회   	|pakring_id=[주차ID],     |
| 배치 관리   | POST		       | /parking/batch   | json        | 배치 실행		     		 	|pakring_id=[주차ID], data_folder=[테스트데이경로]|
|           | GET		       | /parking/batch   | json        | 배치 상태 확인  				|pakring_id=[주차ID]                       |



2.  **동작방식**

2-1.  **모델 생성 규칙**

- [POST] /parking/model API로 모델 생성 요청
- 기계학습 모델 학습이 완료되면 /model 폴더에 주자창 별 폴더 생성
- 해당 폴더 하위에 모델 파일(.model)과 모델 정보 파일(.txt) 저장 
  
2-2.  **배치 실행 규칙**

- [POST] /parking/batch API로 배치 실행 요청
- 'parking_id' 에 해당하는 모델에 대해 1시간 주기로 배칠 실행 요청
- 1시간 주기로 주차 혼잡도 저장
  

2-3. **생성된 모델 저장 구조 예시**
     

```
 "path": "../parking/model", # 모델저장경로
.
├── KETI_Block_A # 주차ID 별 모델저장
│ ├── lgbm.model # 생성된 모델 파일
│ ├── lgbm.txt # 생성된 모델 정보 파일
│ ├── scaler_hourlyRainfall.pickle
│ ├── scaler_humidity.pickle
│ ├── scaler_temperature.pickle
│ └── scaler_windSpeed.pickle
.
├── KETI_Block_B # 주자ID 별 모델저장
│ ├── lgbm.model
│ ├── lgbm.txt
│ ├── scaler_hourlyRainfall.pickle
│ ├── scaler_humidity.pickle
│ ├── scaler_temperature.pickle
│ └── scaler_windSpeed.pickle
.
.
```

      
