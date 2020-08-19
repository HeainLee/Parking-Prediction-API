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
curl -d '{"estimator":"svr"}' \
-H "Content-Type: application/json" \
-X POST http://[host ip]:8000/parking/model
```

#### Batch(Test) step

```bash
curl -X PATCH  http://[host ip]:8000/parking/model/{id}
```

## Additional notes



1.  **API 목록**

1-1.  **API URI 맵**

| **기능구분**		| **HTTP 메서드**| **URI**    		                   | **출력포맷**  | **설명**                               				|
|---------------|---------------|---------------------------------|--------------|----------------------------------------------|
| 모델 관리      | POST			| /parking/model                 		     | json         | 모델 생성                              				|
|              | GET 			| /parking/model             		         | json         | 학습된 모델 조회                   			  	|
|              | GET 			| /parking/model/{id}        		         | json         | 학습된 모델 개별 조회                   			  	|
| 배치 관리      | PATCH		| /parking/model/{id}/status=start       | json         | 모델 id의 배치 실행		     				    	|
|              | PATCH		| /parking/model/{id}/status=stop        | json         | 모델 id의 배치 정지	    				    	|
|              | PATCH		| /parking/model/{id}/status=get         | json         | 모델 id의 배치 수정				    	|
|              | PATCH		| /parking/model/{id}/status=edit        | json         | 모델 id의 배치 상태 확인  				    	|



2.  **모델 생성 규칙**

  > [POST] `/parking/model` API로 모델 생성 요청 </br>
  -> 기계학습 모델 학습이 완료되면 `/model` 폴더에 id를 부여해서 폴더 생성 </br>
  -> 해당 폴더 하위에 모델 파일(.pickle)과 모델 정보(.txt) 저장 
  
2-1. **생성된 모델 저장 구조 예시**
     

```
  {
      "path": "../parking/model", # 모델저장경로 
      "result": {                 # 모델저장정보 모음 (파일구조)
          "모델폴더1": {
              "파일목록1": [
                  "모델이름.model", # 생성된 모델 파일
                  "모델이름.txt"    # 생성된 모델 정보 파일
              ]
          },
          "모델폴더2": {
              "파일목록2": [
                  "모델이름.model",
                  "모델이름.txt"
              ]
          },
          # ...
      }
  }
```

      
