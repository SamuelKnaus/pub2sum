import textwrap

import openai
import pdf2doi
from pypdf import PdfReader
from rouge_score import rouge_scorer

from constants import INSTRUCTION
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
    input_text = ""

    # Only summarize the PDF if the user decided to turn on the switch in the GUI
    if request.form.getlist("summarize_text"):
        print("> Reading text from PDF file...")
        reader = PdfReader(file_path)
        number_of_pages = len(reader.pages)

        # Loop over each page object and write the text into a variable for further processing
        for i in list(range(0, number_of_pages)):
            page = reader.pages[i]
            text = page.extract_text()
            input_text = input_text + '\n' + text
        item["input_text"] = input_text

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
                response = get_text_summary(chunk, "text-davinci-003")
                summary = response.choices[0].text[:-1]
                text_summary = text_summary + " " + summary

            chunks = textwrap.wrap(text_summary, 6000)

        item["summary"] = text_summary + "."
        print("*** Final Summary ***\n" + text_summary)

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


def process_zip_file(request, file):
    return "process zip"


def get_text_summary(request_text, model):
    prompt = INSTRUCTION + "\n\n" + request_text + "###"

    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0.6,
        stop=[" END"]
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
