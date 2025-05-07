from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import pymysql
from pm25 import (
    get_pm25_data_from_mysql,
    updata_db,
    get_cities_name,
    get_data_by_site,
    get_sites,
)
import json

app = Flask(__name__)


@app.route("/pm25-county-site")
def pm25_county_site():
    county = request.args.get("county")
    sites = get_sites(county)
    result = json.dumps(sites, ensure_ascii=False)
    return result


@app.route("/pm25-site")
def pm25_site():
    cities_name = get_cities_name()
    return render_template("pm25-site.html", counties=cities_name)


@app.route("/pm25-data-site")
def pm25_data_by_site():
    county = request.args.get("county")
    site = request.args.get("site")

    if not county or not site:
        result = json.dumps({"error": "縣市跟站點名稱不能為空!"}, ensure_ascii=False)
    else:
        columns, datas = get_data_by_site(county, site)
        df = pd.DataFrame(datas, columns=columns)
        # 轉換字串時間格式
        date = df["datacreationdate"].apply(lambda x: x.strftime("%Y-%m-%d %H"))
        data = {
            "county": county,
            "site": site,
            "x_data": date.to_list(),
            "y_data": df["pm25"].to_list(),
            "higher": df["pm25"].max(),
            "higher": df["pm25"].min(),
        }

        result = json.dumps(data, ensure_ascii=False)

    return result


@app.route("/")
def index():
    # 取得資料庫最新資料
    columns, datas = get_pm25_data_from_mysql()
    # 取出不同縣市給select
    df = pd.DataFrame(datas, columns=columns)
    # 排序縣市
    counties = sorted(df["county"].unique().tolist())

    # 選取縣市後的資料(預設ALL)
    county = request.args.get("county", "ALL")

    if county == "ALL":
        df1 = df.groupby("county")["pm25"].mean().reset_index()
        # 繪製所需資料
        x_data = df1["county"].to_list()

    else:
        # 取得特定縣市的資料
        df = df.groupby("county").get_group(county)
        # 繪製所需資料
        x_data = df["site"].to_list()

    columns = df.columns.tolist()
    datas = df.values.tolist()
    # 繪製所需資料
    y_data = df["pm25"].to_list()

    return render_template(
        "index.html",
        columns=columns,
        datas=datas,
        counties=counties,
        selected_county=county,
        x_data=x_data,
        y_data=y_data,
    )


@app.route("/pm25-data")
def getpm25_data():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    df = pd.read_csv(url)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
    df1 = df.dropna()
    return df1.values.tolist()


@app.route("/updata")
def updata():
    row_count, message = updata_db()
    nowtime = datetime.now().strftime("%Y-%m-%d")
    result = json.dumps(
        {"時間": nowtime, "更新筆數": row_count, "結果": message}, ensure_ascii=False
    )
    return result


@app.route("/books")
def books_page():
    # return f"<h1>Hell World!</h1>\n{datetime.now()}"
    books = []

    if books:
        for book in books:
            print(book["name"])
            print(book["price"])
            print(book["image_url"])
    else:
        print("販售完畢，目前無書籍")
    username = "Danny"
    nowtime = datetime.now().strftime("%Y-%m-%d")
    print(username, nowtime)
    return render_template("books.html", name=username, now=nowtime, books=books)


@app.route("/bmi")
def bmi():
    # arge GET
    height = eval(request.args.get("height"))
    weight = eval(request.args.get("weight"))
    print(height, weight)

    bmi = round(weight / (height / 100) ** 2, 2)

    return render_template("bmi.html", height=height, weight=weight, bmi=bmi)
    # return render_template(**locals)#全部變數都丟


app.run(debug=True)
# if __name__ == "__main__":
#    app.run(debug=True)
