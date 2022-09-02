import os

import openai
from flask import Flask, redirect, render_template, request, url_for

import layoutparser as lp
import cv2

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    raw_text = ""

    if request.method == "POST":
        file_name = request.form["file_name"]
        # pdf_tokens, pdf_images = lp.load_pdf("static/references/" + file_name, load_images=True)
        # image = pdf_images[1]

        image = cv2.imread("static/references/" + file_name)
        image = image[..., ::-1]

        model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                         extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
                                         label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"})
        layout = model.detect(image)
        lp.draw_box(image, layout, box_width=3)

        # layoutparser.elements.Layout

        text_blocks = lp.Layout([b for b in layout if b.type == 'Text'])
        figure_blocks = lp.Layout([b for b in layout if b.type == 'Figure'])

        text_blocks = lp.Layout([b for b in text_blocks
                                 if not any(b.is_in(b_fig) for b_fig in figure_blocks)])

        h, w = image.shape[:2]

        left_interval = lp.Interval(0, w / 2 * 1.05, axis='x').put_on_canvas(image)

        left_blocks = text_blocks.filter_by(left_interval, center=True)
        print(type(left_blocks))
        left_blocks.sort(key=lambda b: b.coordinates[1], inplace=True)

        right_blocks = [b for b in text_blocks if b not in left_blocks]
        print(type(right_blocks))
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

        generate_summary(request_text)

    summary = request.args.get("result")

    raw_text_length = len(raw_text.split())
    raw_text_tokens = raw_text_length * 1.25

    return render_template("index.html",
                           raw_text_length=raw_text_length,
                           raw_text_tokens=raw_text_tokens,
                           raw_text=raw_text,
                           summary=summary)


def generate_summary(text):
    tldr_tag = "\ntl;dr:"
    text += tldr_tag

    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=text,
        temperature=0.1,
        max_tokens=140,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["\n"]
    )

    return redirect(url_for("index", result=response.choices[0].text))
