import os
import shutil

import openai
from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
from werkzeug.utils import secure_filename

from constants import TEMPORARY_FOLDER, EXTRACTION_FOLDER
from helpers import allowed_file
from processing import process_pdf, process_zip

app = Flask(__name__)

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
            print('No file part')
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("No selected file")
        if file and allowed_file(file.filename):
            if file.content_type == "application/pdf":
                if not os.path.isdir(TEMPORARY_FOLDER):
                    os.makedirs(TEMPORARY_FOLDER)

                filename = secure_filename(file.filename)
                file.save(os.path.join(TEMPORARY_FOLDER, filename))

                paragraphs, summary, completion_tokens, reference = \
                    process_pdf(os.path.join(TEMPORARY_FOLDER, filename))

                input_text = [paragraphs]
                summary = [summary]
                reference = [reference]

                shutil.rmtree(TEMPORARY_FOLDER)

                return render_template("summarizer.html",
                                       input_texts=input_text,
                                       completion_tokens=completion_tokens,
                                       summaries=summary,
                                       references=reference)

            if file.content_type == "application/zip":
                extraction_folder = os.path.join(TEMPORARY_FOLDER, EXTRACTION_FOLDER)
                if not os.path.isdir(extraction_folder):
                    os.makedirs(extraction_folder)

                filename = secure_filename(file.filename)
                file.save(os.path.join(TEMPORARY_FOLDER, filename))

                input_texts, summaries, completion_tokens, references = process_zip(
                    os.path.join(TEMPORARY_FOLDER, filename), extraction_folder)

                shutil.rmtree(TEMPORARY_FOLDER)

                return render_template("summarizer.html",
                                       input_texts=input_texts,
                                       completion_tokens=completion_tokens,
                                       summaries=summaries,
                                       references=references)

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
