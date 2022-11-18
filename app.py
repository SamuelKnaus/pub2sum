import os

import openai
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_assets import Environment, Bundle

from constants import SECRET_KEY
from helpers import allowed_file
from processing import process_file

app = Flask(__name__)
app.secret_key = SECRET_KEY

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('main.scss', filters='libsass', output='main.css')
assets.register('scss_all', scss)

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/summarizer", methods=["GET", "POST"])
def summarizer():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash('No file part')
            return redirect(url_for('summarizer'))
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash("Please select a file")
            return redirect(url_for('summarizer'))
        if file and allowed_file(file.filename):
            if file.content_type == "text/plain":
                items = process_file(file)
                return render_template("summarizer.html", items=items)

            flash("Wrong file format. Please upload plain .txt file")
            return redirect(request.url)

        flash("Please select a text file for upload")
        return redirect(request.url)

    return render_template("summarizer.html")


@app.route("/docs/getting-started", methods=["GET"])
def getting_started():
    return render_template("docs/getting_started.html")


@app.route("/docs/how-it-works", methods=["GET"])
def how_it_works():
    return render_template("docs/how_it_works.html")


@app.route("/docs/settings", methods=["GET"])
def settings():
    return render_template("docs/settings.html")


@app.route("/docs/under-the-hood", methods=["GET"])
def under_the_hood():
    return render_template("docs/under_the_hood.html")


@app.route("/examples", methods=["GET"])
def examples():
    return render_template("examples.html")
