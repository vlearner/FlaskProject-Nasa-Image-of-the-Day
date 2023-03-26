from datetime import date
import requests as requests
from flask import Flask, render_template, request

app = Flask(__name__)
today = str(date.today())
base_url = 'https://api.nasa.gov/planetary/apod?'
api_key = 'api_key=DEMO_KEY&date='


@app.route('/', )
def flask_project():
    return render_template("index.html", today=today)


@app.route('/imageoftheday', methods=['POST', 'GET'])
def image_of_the_day():
    global nasa_img_url
    if request.method == 'POST':
        date_pick = request.form.get('date_pick')
        var = api_key + str(date_pick if date_pick is not None else today)
        session_obj = requests.Session()
        data_response = session_obj.get(base_url, params=var, headers={"User-Agent": "Mozilla/5.0"})
        img_url = data_response.json()
        nasa_img_url = img_url["url"]
    return render_template("index.html",
                           nasa_img_url=nasa_img_url)


if __name__ == '__main__':
    app.run()
