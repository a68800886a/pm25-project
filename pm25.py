import pymysql
import pandas as pd


def open_db():
    conn = None
    try:
        conn = pymysql.connect(
            host="127.0.0.1", port=3306, user="root", passwd="12345678", db="demo"
        )
    except Exception as e:
        print("資料庫開啟失敗", e)
    return conn


def get_pm25_data_from_mysql():
    conn = None
    datas = None
    try:
        conn = open_db()
        cur = conn.cursor()
        # sqlstr="select MAX(datacreationdate) from pm25;"
        sqlstr = "select * from pm25 where datacreationdate=(select MAX(datacreationdate) from pm25);"
        cur.execute(sqlstr)
        # print(cur.description)
        columns = [columnsin[0] for columnsin in cur.description]
        datas = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
    return columns, datas


def updata_db():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    conn = None
    datas = None
    row_count = None
    message = None
    try:
        df = pd.read_csv(url)
        df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
        # 清除NULL
        df1 = df.drop(df[df["pm25"].isna()].index)
        # 找出最新時間
        values = df1.values.tolist()
        # 資料庫操作
        conn = open_db()
        cur = conn.cursor()
        sqlstr = """
        insert ignore into pm25(site,county,pm25,datacreationdate,itemunit) 
        values (%s,%s,%s,%s,%s)
        """
        cur.executemany(sqlstr, values)
        row_count = cur.rowcount
        conn.commit()
        print(f"更新{row_count}筆資料成功")
        message = f"更新資料庫成功"
    except Exception as e:
        print(e)
        message = f"更新資料庫失敗"
    finally:
        if conn is not None:
            conn.close()
    return row_count, message


def get_cities_name():
    conn = open_db()
    cur = conn.cursor()
    sqlstr = "select distinct county from pm25;"
    cur.execute(sqlstr)
    datas = cur.fetchall()
    cities_name = [data[0] for data in datas]
    # print(cities_name)
    return cities_name


if __name__ == "__main__":
    get_cities_name()
    """
    conn = open_db()
    print(conn)
    columns, datas = get_pm25_data_from_mysql()
    print(columns)
    """
