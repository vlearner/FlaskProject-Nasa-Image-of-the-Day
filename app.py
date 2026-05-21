from datetime import date
import requests as requests
from flask import Flask, render_template, request

app = Flask(__name__)
today = str(date.today())
base_url = 'https://api.nasa.gov/planetary/apod'
api_key = 'DEMO_KEY'
nasa_img_url = None


@app.route('/')
def flask_project():
    return render_template("index.html", today=today)


@app.route('/imageoftheday', methods=['POST', 'GET'])
def image_of_the_day():
    global nasa_img_url
    error_msg = None
    if request.method == 'POST':
        date_pick = request.form.get('date_pick')
        selected_date = str(date_pick if date_pick is not None else today)
        params = {'api_key': api_key, 'date': selected_date}
        try:
            session_obj = requests.Session()
            data_response = session_obj.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            img_data = data_response.json()
            if 'url' in img_data:
                nasa_img_url = img_data['url']
            else:
                error_msg = img_data.get('msg', 'No image available for the selected date.')
                nasa_img_url = None
        except Exception:
            error_msg = 'Failed to fetch image from NASA API.'
            nasa_img_url = None
    return render_template("index.html",
                           nasa_img_url=nasa_img_url,
                           error_msg=error_msg,
                           today=today)


if __name__ == '__main__':
    app.run()
