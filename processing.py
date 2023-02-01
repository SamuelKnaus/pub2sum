import textwrap
import pdf2doi

import openai
from pypdf import PdfReader
from rouge_score import rouge_scorer

from constants import INSTRUCTION, DEFAULT_MODEL, FINE_TUNED_MODEL
from references import get_references


def process_pdf_file(request, file_path):
    items = []
    item = {
        "input_text": None,
        "summary": None,
        "first_reference": None,
        "continuing_reference": None,
        "reference_list_entry": None
    }
    paper = ["", "", ""]

    print("Processing PDF file...")

    if request.form.getlist("summarize_text"):
        reader = PdfReader(file_path)
        number_of_pages = len(reader.pages)

        for i in list(range(0, number_of_pages)):
            page = reader.pages[i]
            text = page.extract_text()
            paper[0] = paper[0] + '\n' + text
        item["input_text"] = paper[0]

        level = 1
        while level < 3:
            print("-Level " + str(level) + "-")
            chunks = textwrap.wrap(paper[level - 1], 6000)
            for index, chunk in enumerate(chunks):
                print("Processing level " + str(level) + " chunk " + str(index))
                if request.form.getlist("use_fine_tuned_model"):
                    response = get_text_summary(chunk, FINE_TUNED_MODEL)
                else:
                    response = get_text_summary(chunk, DEFAULT_MODEL)
                summary = response.choices[0].text[:-1]
                paper[level] = paper[level] + " " + summary
            level += 1
        item["summary"] = paper[2]
        print("*** Final Summary ***\n" + paper[2])

    if request.form.getlist("fetch_references"):
        pdf2doi.config.set("verbose", False)
        results = pdf2doi.pdf2doi(file_path)
        first_reference, continuing_reference, reference_list_entry = get_references(results["identifier"])
        item["first_reference"] = first_reference
        item["continuing_reference"] = continuing_reference
        item["reference_list_entry"] = reference_list_entry

    items.append(item)

    return items


def process_zip_file(request, file):
    return "process zip"


def get_text_summary(request_text, model):
    prompt = INSTRUCTION + "\n\n" + request_text + "\n\n###\n\n"
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0.6,
        stop=["###", "\n\n###\n\n"]
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
