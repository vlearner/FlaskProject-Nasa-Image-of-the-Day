from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def flask_project():  # put application's code here
    return render_template("index.html")


@app.route('/name', methods=['POST'])
def name_page():
    return render_template(
        "name.html",
        name=request.form['name'],
        last_name=request.form['last_name']
    )


if __name__ == '__main__':
    app.run()
