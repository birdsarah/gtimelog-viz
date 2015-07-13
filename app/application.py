#! /usr/bin/env python

from flask import Flask

from utils.embed_charts import assemble


app = Flask(__name__)


@app.route("/")
def main():
    rendered_html = assemble()
    return rendered_html

if __name__ == "__main__":
    app.run(debug=True)
