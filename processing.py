import openai

from constants import SUMMARIZE, REFERENCES, DELIMITER
from references import get_references
from rouge_score import rouge_scorer


def process_file(file):
    raw_text = file.read().decode("utf-8")
    texts = raw_text.split(DELIMITER)
    items = []

    for index, text in enumerate(texts):
        item = {
            "input_text": None,
            "summary": None,
            "completion_tokens": None,
            "reference": None,
            "reference_short": None,
            "reference_list": None
        }

        identifier, text = text.strip().split("\n", 1)
        item["input_text"] = text

        if SUMMARIZE:
            response = get_text_summary(text)
            summary = response.choices[0].text[:-1]
            completion_tokens = response.usage.completion_tokens

            item["summary"] = summary
            item["completion_tokens"] = completion_tokens

        if REFERENCES:
            first_reference, continuing_reference, reference_list_entry = get_references(identifier)

            item["first_reference"] = first_reference
            item["continuing_reference"] = continuing_reference
            item["reference_list_entry"] = reference_list_entry

        items.append(item)

    return items


def get_text_summary(request_text):
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=request_text,
        temperature=0,
        max_tokens=200
    )
    return response


def calculate_scores(reference_summary, generated_summary):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)

    return scores
