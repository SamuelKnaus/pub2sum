import json
import os
import urllib.request
from urllib.error import HTTPError

import layoutparser as lp
import numpy as np
import openai
import pdf2doi
from flask import Flask, render_template, request

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

pdf2doi.config.set('verbose', False)
debug = True


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/documentation", methods=["GET"])
def documentation():
    return render_template("documentation.html")


@app.route("/summarizer", methods=["GET", "POST"])
def summarizer():
    raw_text = ""
    completion_tokens = ""
    summary = ""
    reference_list = ""

    if request.method == "POST":
        file_name = request.form["file_name"]
        file_path = "static/references/" + file_name

        pdf_layout, pdf_images = lp.load_pdf(file_path, load_images=True)
        image = np.array(pdf_images[0])

        model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                         extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                         label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"})
        layout = model.detect(image)
        lp.draw_box(image, layout, box_width=3)

        # layoutparser.elements.Layout

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

        request_text = ""
        for txt in text_blocks.get_texts():
            request_text += txt
            raw_text += "<p>" + txt + "</p>"

        tldr_tag = "\ntl;dr:"
        request_text += tldr_tag

        # response = openai.Completion.create(
        #    model="text-davinci-002",
        #    prompt=request_text,
        #    temperature=0,
        #    max_tokens=200
        # )
        # summary = response.choices[0].text[:-1]
        # completion_tokens = response.usage.completion_tokens

        references = get_references(file_path)
        summary += " " + references[0]
        reference_list += references[1]

    raw_text_word_count = len(raw_text.split())
    raw_text_tokens = raw_text_word_count * 1.25

    output_word_count = len(summary.split())

    return render_template("summarizer.html",
                           raw_text_word_count=raw_text_word_count,
                           raw_text_tokens=raw_text_tokens,
                           raw_text=raw_text,
                           output_word_count=output_word_count,
                           completion_tokens=completion_tokens,
                           summary=summary,
                           reference_list=reference_list)


def get_references(file_path):
    information = pdf2doi.pdf2doi(file_path)
    identifier_type = information["identifier_type"]
    identifier = information["identifier"]

    references = fetch_bibliography(identifier_type, identifier)

    if references:
        return references

    return "Could not find reference!"


def fetch_bibliography(identifier_type, identifier):
    if identifier_type == "DOI":
        inline_item = "Could not find reference for " + identifier
        bibliography_item = "Could not find reference for " + identifier
        request_url = "https://doi.org/" + identifier

        bib_request = urllib.request.Request(request_url)
        bib_request.add_header('Accept', 'text/x-bibliography')
        bib_request.add_header('style', 'apa-6th-edition')

        inline_request = urllib.request.Request(request_url)
        inline_request.add_header('Accept', 'application/vnd.citationstyles.csl+json')

        try:
            with urllib.request.urlopen(bib_request) as f:
                bibliography_item = f.read().decode()

            with urllib.request.urlopen(inline_request) as f:
                inline_response = json.loads(f.read().decode())
                authors = inline_response["author"]
                if len(authors) == 1:
                    inline_item = " (" + authors[0]["family"] + ", " \
                                  + str(inline_response["published-print"]["date-parts"][0][0]) + ")."

                if len(authors) == 2:
                    inline_item = " (" + authors[0]["family"] + " & " + authors[1]["family"] + ", " \
                                  + str(inline_response["published-print"]["date-parts"][0][0]) + ")."

                if len(authors) > 2:
                    inline_item = " (" + authors[0]["family"] + " et al., " \
                                  + str(inline_response["published-print"]["date-parts"][0][0]) + ")."
        except HTTPError as e:
            if e.code == 404:
                print('DOI not found.')
            else:
                print('Service unavailable.')

        return inline_item, bibliography_item

    if identifier_type == "arxiv ID":
        # request_url = "http://export.arxiv.org/api/query?id_list=" + identifier
        # response = urllib.request.urlopen(request_url)
        # dictionary = xmltodict.parse(response.read())

        # title = dictionary["feed"]["entry"]["title"]
        title = "arXiv reference - work in progress"

        return title

    return None
