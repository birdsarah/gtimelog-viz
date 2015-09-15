#! /usr/bin/env python

import datetime

from flask import Flask, request

from utils.embed_charts import assemble, assemble_timesheet

app = Flask(__name__)

get_time = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')


@app.route("/")
@app.route("/<date>/")
def main(date=None):
    try:
        today = get_time(date)
        today = today + datetime.timedelta(days=1) - datetime.timedelta(minutes=1)  # We want it to be the end of the day
    except (TypeError, ValueError):
        today = datetime.datetime.today()
    rendered_html = assemble(today)
    return rendered_html


@app.route("/timesheet/")
def timesheet():
    start = get_time(request.args.get('start'))
    end = request.args.get('end')
    if end:
        end = get_time(request.args.get('end'))
    else:
        end = start + datetime.timedelta(days=6)
    rendered_timesheet = assemble_timesheet(start, end)
    return rendered_timesheet


if __name__ == "__main__":
    app.run(debug=True, port=5001)
