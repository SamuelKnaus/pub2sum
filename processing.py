import openai
from rouge_score import rouge_scorer

from constants import DELIMITER, INSTRUCTION
from references import get_references


def process_file(request, file):
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

        if (request.form.getlist("summarize_text") and request.cookies.get("summarize_text")) or (
                request.form.getlist("summarize_text") and not request.cookies.get("summarize_text")):

            if request.form.getlist("use_fine_tuned_model") and request.cookies.get("use_fine_tuned_model") or (
                    request.form.getlist("use_fine_tuned_model") and not request.cookies.get("use_fine_tuned_model")):
                print("Using custom [davinci:ft-personal:master-500-2023-01-12-12-09-28]")
                model = "davinci:ft-personal:master-500-2023-01-12-12-09-28"
            else:
                print("Using standard [text-davinci-003]")
                model = "text-davinci-003"

            response = get_text_summary(text, model)

            summary = response.choices[0].text[:-1]
            completion_tokens = response.usage.completion_tokens

            item["summary"] = summary
            item["completion_tokens"] = completion_tokens

        if request.form.getlist("fetch_references") and request.cookies.get("fetch_references") or (
                request.form.getlist("fetch_references") and not request.cookies.get("fetch_references")):
            first_reference, continuing_reference, reference_list_entry = get_references(identifier)

            item["first_reference"] = first_reference
            item["continuing_reference"] = continuing_reference
            item["reference_list_entry"] = reference_list_entry

        items.append(item)

    return items


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
        stop="\n\n###\n\n"
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
