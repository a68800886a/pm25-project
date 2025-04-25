from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import pymysql

app = Flask(__name__)


@app.route("/")
def index():
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
    return render_template("index.html", name=username, now=nowtime, books=books)


@app.route("/pm25-data")
def getpm25_data():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=CSV"
    df = pd.read_csv(url)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"])
    df1 = df.dropna()
    return df1.values.tolist()


@app.route("/bmi")
def bmi():
    # arge GET
    height = eval(request.args.get("height"))
    weight = eval(request.args.get("weight"))
    print(height, weight)

    bmi = round(weight / (height / 100) ** 2, 2)

    return render_template("bmi.html", height=height, weight=weight, bmi=bmi)


app.run(debug=True)
# if __name__ == "__main__":
#    app.run(debug=True)
