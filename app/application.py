#! /usr/bin/env python

from flask import Flask

from process_gtimelog import get_raw_df
from embed_charts import assemble


app = Flask(__name__)


@app.route("/")
def main():
    raw = get_raw_df()
    rendered_html = assemble(raw)
    return rendered_html

if __name__ == "__main__":
    app.run(debug=True)
