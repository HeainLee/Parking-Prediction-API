import psycopg2
import sys


def load_trainset():
    # ================== Database Connection ===================
    conn_string = "host='182.252.135.134' dbname ='postgres' user='daumsoft' password='daumsoft'"

    try:
        conn = psycopg2.connect(conn_string)
    except:
        print "error database connection"
    curs = conn.cursor()

    # ================== SQL Execute ===================
    # sql_string = "SELECT * FROM cityhub.tmlnavlparkingspot"

    sql_string = \
        "select	id, parkingdate, timeslot, dayofweek, pm10value, pm25value, airqualitylevel,\n" \
        "		temperature, rainfall, hourlyrainfall, snowfall, weathertype, avgavlspot\n" \
        "from	cityhub.tmlnavlparkingspot"
    curs.execute(sql_string)
    result = curs.fetchall()
    conn.commit()
    return result


if __name__ == '__main__':
    result = load_trainset()
    print result
