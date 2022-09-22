import os
from zipfile import ZipFile

import layoutparser as lp
import numpy as np
import openai

from constants import LAYOUT_MODEL, EXTRA_CONFIG, LABEL_MAP, SUMMARIZE, REFERENCES
from references import get_references


def process_pdf(file_path):
    print("Processing " + file_path + "...")

    item = []
    input_text = ""
    summary = ""
    completion_tokens = 0
    references = ""
    paragraphs = []

    model = lp.Detectron2LayoutModel(LAYOUT_MODEL, extra_config=EXTRA_CONFIG, label_map=LABEL_MAP)

    pdf_tokens, pdf_images = lp.load_pdf(file_path, load_images=True, dpi=216)

    for image in pdf_images:
        image = np.array(image)
        text_blocks = get_text_from_image(model, image)

        page_paragraphs = text_blocks.get_texts()

        paragraphs.append(page_paragraphs)

        for page_paragraph in page_paragraphs:
            input_text += page_paragraph

    if SUMMARIZE:
        response = generate_summary_from_text(input_text + "\ntl;dr:")

        summary = response.choices[0].text[:-1]
        completion_tokens = response.usage.completion_tokens

    if REFERENCES:
        reference_items = get_references(file_path)
        summary += " " + reference_items[0]
        references += reference_items[1]

    item.extend([paragraphs, summary, completion_tokens, references])

    print(file_path + " processed successfully.")

    return item


def process_zip(file_path, extraction_path):
    print("Processing " + file_path + "...")

    items = []
    input_texts = []
    summaries = []
    completion_tokens = 0
    references = []

    with ZipFile(file_path, 'r') as zipObj:
        zipObj.extractall(path=extraction_path)

    for pdf in os.listdir(extraction_path):
        current_file_path = os.path.join(extraction_path, pdf)
        # checking if it is a file
        if os.path.isfile(current_file_path):
            current_paragraphs, current_summary, current_completion_tokens, current_references = process_pdf(
                current_file_path)
            if current_paragraphs:
                input_texts.append(current_paragraphs)
            if current_summary:
                summaries.append(current_summary)
            if current_completion_tokens:
                completion_tokens += current_completion_tokens
            if current_references:
                references.append(current_references)

    references = sorted(references)
    items.extend([input_texts, summaries, completion_tokens, references])

    print(file_path + " processed successfully.")

    return items


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
