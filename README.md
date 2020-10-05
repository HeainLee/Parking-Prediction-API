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
curl -d '{"data_path":"home/path/data/trainData.json}' \
-H "Content-Type: application/json" \
-X POST http://[host ip]:8000/parking/model
```

#### Batch(Test) step

```bash
curl -d '{"data_path":"home/path/data/testData.json, "model_name":"rfr"}' \
-H "Content-Type: application/json" \
-X POST http://[host ip]:8000/parking/batch
```

## Additional notes



1.  **API 목록**

1-1.  **API URI 맵**

| **기능구분**	| **HTTP 메서드**| **URI**    		  | **출력포맷**  | **설명**              | **파라미터**                            |
|----------|--------------|------------------|-------------|---------------------|---------------------------------------|
| 모델 관리   | POST			     | /parking/model   | json        | 모델 생성             |data_path=[데이터경로]                    |
|           | GET 			   | /parking/model   | json        | 학습된 모델 조회        |                                       |
|           | GET 			   | /parking/model   | json        | 학습된 모델 상세 조회   	|p_id=[주차장ID], file_name=[모델정보파일]     |
| 배치 관리   | POST		       | /parking/batch   | json        | 배치 실행		     		 	|data_path=[데이터경로], model_name=[모델이름]}|
|           | GET		       | /parking/batch   | json        | 배치 상태 확인  				|                                        |



2.  **모델 생성 규칙**

  > [POST] `/parking/model` API로 모델 생성 요청 </br>
  -> 기계학습 모델 학습이 완료되면 `/model` 폴더에 주자명 면적 당 폴더 생성 </br>
  -> 해당 폴더 하위에 모델 파일(.model)과 모델 정보 파일(.txt) 저장 
  
2-1. **생성된 모델 저장 구조 예시**
     

```
  {
      "path": "../parking/model", # 모델저장경로 
      "result": {                 # 모델저장정보 모음 (파일구조)
          "모델폴더1(주차장01)": {
                  "모델이름.model", # 생성된 모델 파일
                  "모델이름.txt"    # 생성된 모델 정보 파일
          },
          "모델폴더2(주차장02)": {
                  "모델이름.model",
                  "모델이름.txt"
          },
 
          ...
      }
  }
```

      
