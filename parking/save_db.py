import json
from os import listdir
from os.path import isfile, join
from pandas import json_normalize


data_path = '../../data.json'
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
get_files = []
for file in onlyfiles:
    if file.startswith('2020'):
        get_files.append(file)

print(len(get_files))

for files in get_files:
    data = data_path + '/' + files
    with open(data, encoding="utf-8") as data_file:    
        df_parking = json_normalize(json.load(data_file),sep='_')

    df_parking = df_parking.drop(['prediction'],axis=1)
    df_parking.rename(columns = lambda c: c.split('_')[1] if 'observation_'in c else c, inplace = True)
    before_len_row = df_parking.shape[0]
    df_parking = df_parking.drop_duplicates()
    after_len_row = df_parking.shape[0]

    if before_len_row != after_len_row:
        print("delete duplicate row!", before_len_row, '=>', after_len_row)

    import psycopg2
    from psycopg2.errors import UniqueViolation
    conn = psycopg2.connect(host='local..', dbname='hea..', user='hea..', password='hea..', port='5432')
    cur = conn.cursor()

    create_exc = """CREATE TABLE IF NOT EXISTS parking_schema.parking_a ( 
        id varchar(50) NOT NULL 
        , dateTime timestamp NOT NULL 
        , isHoliday boolean NOT NULL 
        , totalSpotNumber integer NOT NULL 
        , availableSpotNumber integer NOT NULL 
        , temperature real NOT NULL 
        , hourlyRainfall real NOT NULL 
        , windSpeed real NOT NULL 
        , weatherType varchar(50) 
        , humidity integer NOT NULL
        , PRIMARY KEY(dateTime) 
    );"""


    cur.execute(create_exc)
    conn.commit()

    cols = ([str(i) for i in df_parking.columns.tolist()])

    try:
        # Insert Dataframe into SQL Server:
        for index, row in df_parking.iterrows():
            # "INSERT INTO parking_schema.parking_a ('" +cols + "') VALUES (" + "%s,"*(len(row)-1) + "%s)"
            sql = "INSERT INTO parking_schema.parking_a \
            (id, dateTime, isHoliday, totalSpotNumber, availableSpotNumber, temperature, \
            hourlyRainfall, windSpeed, weatherType, humidity) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, tuple(row))
    except UniqueViolation as e:
        # print(e)
        continue

    conn.commit()
    cur.close()
    conn.close()
    print(' ')
print('end save!')