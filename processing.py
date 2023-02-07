import textwrap

import layoutparser as lp
import numpy as np
import openai
import pdf2doi
from rouge_score import rouge_scorer

from constants import FIRST_INSTRUCTION, LAYOUT_MODEL, EXTRA_CONFIG, LABEL_MAP, FINAL_INSTRUCTION
from references import get_references


def process_pdf_file(request, file_path):
    print("Processing " + request.files["file"].filename)
    items = []
    item = {
        "input_text": None,
        "summary": None,
        "first_reference": None,
        "continuing_reference": None,
        "reference_list_entry": None
    }

    input_text = get_raw_text(file_path)
    item["input_text"] = input_text

    # Only summarize the PDF if the user decided to turn on the switch in the GUI
    if request.form.getlist("summarize_text"):
        # Split the text into chunks that the API can handle and summarize each chunk.
        # Iterate this procedure until only 1 chunk is left. Then create the final summary.
        print("> Summarizing text from PDF...")
        level = 0
        text_summary = input_text
        chunks = textwrap.wrap(text_summary, 6000)

        while len(chunks) > 1:
            text_summary = ""

            for index, chunk in enumerate(chunks):
                print("Processing level " + str(level) + " chunk " + str(index))
                response = get_text_summary(FIRST_INSTRUCTION, input_text=chunk, model="text-davinci-003", max_tokens=400)
                summary = response.choices[0].text[:-1]
                text_summary = text_summary + " " + summary

            chunks = textwrap.wrap(text_summary, 6000)
            level += 1

        # Request final summary when only one chunk is left
        print("Processing level " + str(level) + " chunk 0")
        response = get_text_summary(FINAL_INSTRUCTION, input_text=chunks[0], model="text-davinci-003", max_tokens=300)
        summary = response.choices[0].text[:-1]

        item["summary"] = summary + "."
        print("*** Final Summary ***" + summary)

    # Only fetch references if the user decided to turn on the switch in the GUI
    if request.form.getlist("fetch_references"):
        pdf2doi.config.set("verbose", False)
        results = pdf2doi.pdf2doi(file_path)
        first_reference, continuing_reference, reference_list_entry = get_references(results["identifier"])
        item["first_reference"] = first_reference
        item["continuing_reference"] = continuing_reference
        item["reference_list_entry"] = reference_list_entry

    items.append(item)

    return items


def get_raw_text(file_path):
    input_text = ""

    model = lp.Detectron2LayoutModel(LAYOUT_MODEL, extra_config=EXTRA_CONFIG, label_map=LABEL_MAP)
    ocr_agent = lp.TesseractAgent(languages='eng')

    pdf_tokens, pdf_images = lp.load_pdf(file_path, load_images=True, dpi=216)

    for image in pdf_images:
        image = np.array(image)
        text_blocks = get_text_from_image(model, image, ocr_agent)

        page_paragraphs = text_blocks.get_texts()

        for page_paragraph in page_paragraphs:
            input_text += page_paragraph

    return input_text


def get_text_from_image(model, image, ocr_agent):
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

    for block in text_blocks:
        segment_image = (block
                         .pad(left=5, right=5, top=5, bottom=5)
                         .crop_image(image))

        text = ocr_agent.detect(segment_image)
        block.set(text=text, inplace=True)

    return text_blocks


def process_zip_file(request, file):
    return "process zip"


def get_text_summary(instruction, input_text, model, max_tokens=500):
    prompt = instruction + "\n\n" + "Text: ###\n" + input_text + "\n###"

    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0.6
    )

    return response


def calculate_scores(reference_summary, generated_summary):
    result_item = {
        "reference_summary": reference_summary,
        "generated_summary": generated_summary,
        "scores": None
    }

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)

    result_item["scores"] = scores

    return result_item
