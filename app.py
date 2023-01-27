import os

import openai
from flask import Flask, flash, request, redirect, url_for, render_template, make_response
from flask_assets import Environment, Bundle
from werkzeug.utils import secure_filename

from constants import SECRET_KEY, TEMPORARY_FOLDER
from helpers import allowed_file
from processing import process_text_file, process_pdf_file , calculate_scores

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
                items = process_text_file(request, file)
                response = make_response(render_template("summarizer.html", items=items))
                return response

            if file.content_type == "application/pdf":
                if not os.path.isdir(TEMPORARY_FOLDER):
                    os.makedirs(TEMPORARY_FOLDER)

                filename = secure_filename(file.filename)
                file.save(os.path.join(TEMPORARY_FOLDER, filename))

                items = process_pdf_file(request, os.path.join(TEMPORARY_FOLDER, filename))

                response = make_response(render_template("summarizer.html", items=items))

                return response

            flash("Wrong file format. Please upload plain .txt file")
            return redirect(request.url)

        flash("Please select a text file for upload")
        return redirect(request.url)

    return render_template("summarizer.html",
                           summarize_text=request.cookies.get("summarize_text"),
                           fetch_references=request.cookies.get("fetch_references"),
                           use_fine_tuned_model=request.cookies.get("use_fine_tuned_model"))


@app.route("/rouge", methods=["GET", "POST"])
def rouge():
    if request.method == "POST":
        reference_summary = request.form["reference-summary"]
        generated_summary = request.form["generated-summary"]

        if not reference_summary:
            flash("Please provide a summary for reference")
            return redirect(request.url)

        if not generated_summary:
            flash("Please provide a generated summary")
            return redirect(request.url)

        result_item = calculate_scores(reference_summary, generated_summary)

        return render_template("rouge.html", result_item=result_item)

    return render_template("rouge.html")


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
