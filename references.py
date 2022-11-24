import json
import requests


def get_references(identifier):
    reference, reference_short, reference_list = fetch_bibliography(identifier)

    if reference or reference_short or reference_list:
        return reference, reference_short, reference_list

    return "Could not find reference(s)."


def fetch_bibliography(identifier):
    first_reference = ""
    continuing_reference = ""
    reference_list_entry = ""
    request_url = identifier

    reference_headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    reference_request = requests.get(request_url, headers=reference_headers)

    if reference_request.text:
        reference_response = json.loads(reference_request.text)
        authors = reference_response["author"]

        # First Reference
        if len(authors) >= 6:
            first_reference = authors[0]["family"] + " et al., " + str(
                reference_response["published-print"]["date-parts"][0][0])
        else:
            for index, author in enumerate(authors):
                if index == len(authors) - 1 and len(authors) > 1:
                    first_reference += " & " + author["family"]
                else:
                    if index == 0:
                        first_reference += author["family"]
                    else:
                        first_reference += ", " + author["family"]
            first_reference += ", " + str(reference_response["published-print"]["date-parts"][0][0])

        # Continuing reference
        if len(authors) == 1:
            continuing_reference = authors[0]["family"] + ", " + str(
                reference_response["published-print"]["date-parts"][0][0])

        if len(authors) == 2:
            continuing_reference = authors[0]["family"] + " & " + authors[1]["family"] + ", " + str(
                reference_response["published-print"]["date-parts"][0][0])

        if len(authors) > 2:
            continuing_reference = authors[0]["family"] + " et al., " + str(
                reference_response["published-print"]["date-parts"][0][0])

    # Reference list entry
    reference_list_entry_headers = {"Accept": "text/x-bibliography", "style": "apa-6th-edition"}
    reference_list_entry_request = requests.get(request_url, headers=reference_list_entry_headers)
    if reference_list_entry_request.text:
        reference_list_entry = str(reference_list_entry_request.content.decode("utf-8"))

    return first_reference, continuing_reference, reference_list_entry
