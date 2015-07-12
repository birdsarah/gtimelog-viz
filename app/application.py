#! /usr/bin/env python

from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)
