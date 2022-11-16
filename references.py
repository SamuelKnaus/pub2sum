import json
import requests


def get_references(identifier):
    reference, reference_short, reference_list = fetch_bibliography(identifier)

    if reference or reference_short or reference_list:
        return reference, reference_short, reference_list

    return "Could not find reference(s)."


def fetch_bibliography(identifier):
    reference = ""
    reference_short = ""
    reference_list = ""
    request_url = identifier

    # Reference
    reference_headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    reference_request = requests.get(request_url, headers=reference_headers)
    if reference_request.text:
        reference_response = json.loads(reference_request.text)
        authors = reference_response["author"]

        if len(authors) == 1:
            reference = " (" + authors[0]["family"] + ", " \
                          + str(reference_response["published-print"]["date-parts"][0][0]) + ")."

        if len(authors) == 2:
            reference = " (" + authors[0]["family"] + " & " + authors[1]["family"] + ", " \
                          + str(reference_response["published-print"]["date-parts"][0][0]) + ")."

        if len(authors) > 2:
            reference = " (" + authors[0]["family"] + " et al., " \
                          + str(reference_response["published-print"]["date-parts"][0][0]) + ")."

    # Reference short
    reference_short = "et. al TBD"

    # Reference list
    reference_list_headers = {"Accept": "text/x-bibliography", "style": "apa-6th-edition"}
    reference_list_request = requests.get(request_url, headers=reference_list_headers)
    if reference_list_request.text:
        reference_list = str(reference_list_request.content.decode("utf-8"))

    return reference, reference_short, reference_list
