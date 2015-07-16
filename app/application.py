#! /usr/bin/env python

import datetime

from flask import Flask

from utils.embed_charts import assemble

app = Flask(__name__)


@app.route("/")
@app.route("/<date>/")
def main(date=None):
    try:
        today = datetime.datetime.strptime(date, '%Y-%m-%d')
    except (TypeError, ValueError):
        today = datetime.datetime.today()
    rendered_html = assemble(today)
    return rendered_html

if __name__ == "__main__":
    app.run(debug=True)
