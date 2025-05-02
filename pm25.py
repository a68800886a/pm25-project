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
    columns = None
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


# 取得對應縣市的site資料
def get_data_by_site(county, site):
    conn = None
    datas = None
    columns = None
    try:
        conn = open_db()
        cur = conn.cursor()
        sqlstr = "select * from pm25 where county=%s and site=%s;"
        cur.execute(sqlstr, (county, site))
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
    conn = None
    datas = None
    try:
        conn = open_db()
        cur = conn.cursor()
        # 改成只要最新的?
        sqlstr = "select distinct county from pm25;"
        cur.execute(sqlstr)
        datas = cur.fetchall()
        cities_name = [data[0] for data in datas]
    except Exception as e:
        print(e)
        message = f"資料庫失敗"
    finally:
        if conn is not None:
            conn.close()
    # print(cities_name)
    return cities_name


def get_sites(city):
    conn = None
    datas = None
    try:
        conn = open_db()
        cur = conn.cursor()
        # 改成只要最新的?
        sqlstr = "select distinct site from pm25 where county=%s;"
        cur.execute(sqlstr, (city,))
        datas = cur.fetchall()
        sites = [data[0] for data in datas]
    except Exception as e:
        print(e)
        message = f"資料庫失敗"
    finally:
        if conn is not None:
            conn.close()
    # print(cities_name)
    return sites


if __name__ == "__main__":
    columns, datas = get_data_by_site("新北市", "富貴角")
    print(get_sites("新北市"))
