import openai

from constants import SUMMARIZE, REFERENCES


def process_text(input_text):
    items = []
    input_texts = input_text.split("/******/")

    for index, input_text in enumerate(input_texts):
        item = []

        if SUMMARIZE:
            response = get_text_summary(input_text)
            summary = response.choices[0].text[:-1]
            completion_tokens = response.usage.completion_tokens

            item.extend([input_text, summary, completion_tokens])

        if REFERENCES:
            reference = "Referenz #" + str(index)
            item.append(reference)

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
