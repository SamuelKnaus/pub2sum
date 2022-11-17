import openai

from constants import SUMMARIZE, REFERENCES, DELIMITER
from references import get_references


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

        if SUMMARIZE:
            response = get_text_summary(text)
            summary = response.choices[0].text[:-1]
            completion_tokens = response.usage.completion_tokens

            item["input_text"] = text
            item["summary"] = summary
            item["completion_tokens"] = completion_tokens

        if REFERENCES:
            reference, reference_short, reference_list = get_references(identifier)

            item["reference"] = reference
            item["reference_short"] = reference_short
            item["reference_list"] = reference_list

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
