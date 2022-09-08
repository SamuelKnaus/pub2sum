import os

import layoutparser as lp
import numpy as np
import openai
from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
from pdf2image import convert_from_bytes
from werkzeug.utils import secure_filename

from constants import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, LAYOUT_MODEL, EXTRA_CONFIG, LABEL_MAP
from references import get_references

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('main.scss', filters='libsass', output='main.css')
assets.register('scss_all', scss)

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/examples", methods=["GET"])
def examples():
    return render_template("examples.html")


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
            # Temporarily save file for pdf2doi
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print(type(file))

            if file.content_type == "application/pdf":
                html_input_text, summary, completion_tokens, reference_list = process_pdf(file, os.path.join(
                    app.config["UPLOAD_FOLDER"], filename))
                output_word_count = len(summary.split())

                return render_template("summarizer.html",
                                       html_input_text=html_input_text,
                                       output_word_count=output_word_count,
                                       completion_tokens=completion_tokens,
                                       summary=summary,
                                       reference_list=reference_list)

            if file.content_type == "application/zip":
                print("Processing ZIP archive...")
                process_zip(file)

    return render_template("summarizer.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_pdf(file, file_path):
    print("Processing single PDF file...")

    request_text = ""
    html_input_text = ""
    reference_list = ""
    tldr_tag = "\ntl;dr:"

    model = lp.Detectron2LayoutModel(LAYOUT_MODEL, extra_config=EXTRA_CONFIG, label_map=LABEL_MAP)

    pdf = file.read()
    print(type(pdf))
    images = convert_from_bytes(pdf)
    print(type(images))
    # for no, image in enumerate(images):

    image = np.array(images[0])
    text_blocks = get_text_from_image(model, image)

    for txt in text_blocks.get_texts():
        request_text += txt
        html_input_text += "<p>" + txt + "</p>"
    request_text += tldr_tag

    response = generate_summary_from_text(request_text)
    summary = response.choices[0].text[:-1]
    completion_tokens = response.usage.completion_tokens
    references = get_references(file_path)
    summary += " " + references[0]
    reference_list += references[1]

    print("Single PDF processed successfully.")

    return html_input_text, summary, completion_tokens, reference_list


def process_zip(file):
    print("ZIP archive processed successfully.")


def get_text_from_image(model, image):
    layout = model.detect(image)
    lp.draw_box(image, layout, box_width=3)

    text_blocks = lp.Layout([b for b in layout if b.type == 'Text' or b.type == 'Title'])
    figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])
    text_blocks = lp.Layout([b for b in text_blocks
                             if not any(b.is_in(b_fig) for b_fig in figure_blocks)])

    h, w = image.shape[:2]

    left_interval = lp.Interval(0, w / 2 * 1.05, axis='x').put_on_canvas(image)
    left_blocks = text_blocks.filter_by(left_interval, center=True)
    left_blocks.sort(key=lambda b: b.coordinates[1], inplace=True)

    right_blocks = [b for b in text_blocks if b not in left_blocks]
    # right_blocks.sort(key=lambda b: b.coordinates[1], inplace=True)
    right_blocks.sort(key=lambda b: b.coordinates[1])

    text_blocks = lp.Layout([b.set(id=idx) for idx, b in enumerate(left_blocks + right_blocks)])

    lp.draw_box(image, text_blocks,
                box_width=3,
                show_element_id=True)

    ocr_agent = lp.TesseractAgent(languages='eng')

    for block in text_blocks:
        segment_image = (block
                         .pad(left=5, right=5, top=5, bottom=5)
                         .crop_image(image))

        text = ocr_agent.detect(segment_image)
        block.set(text=text, inplace=True)

    return text_blocks


def generate_summary_from_text(request_text):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=request_text,
        temperature=0,
        max_tokens=200
    )

    return response
