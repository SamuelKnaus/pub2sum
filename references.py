import json

import pdf2doi
import requests


def get_references(file_path):
    information = pdf2doi.pdf2doi(file_path)
    identifier_type = information["identifier_type"]
    identifier = information["identifier"]

    references = fetch_bibliography(identifier_type, identifier)

    if references:
        return references

    return "Could not find reference(s)."


def fetch_bibliography(identifier_type, identifier):
    if identifier_type == "DOI":
        inline_item = "(Could not find reference for " + identifier + ")"
        bib_item = "Could not find reference for " + identifier + ""
        request_url = "https://dx.doi.org/" + identifier

        bib_headers = {"Accept": "text/x-bibliography", "style": "apa-6th-edition"}
        bib_request = requests.get(request_url, headers=bib_headers)
        if bib_request.text:
            bib_item = str(bib_request.content.decode("utf-8"))

        inline_headers = {"Accept": "application/vnd.citationstyles.csl+json"}
        inline_request = requests.get(request_url, headers=inline_headers)
        if inline_request.text:
            inline_response = json.loads(inline_request.text)
            authors = inline_response["author"]

            if len(authors) == 1:
                inline_item = " (" + authors[0]["family"] + ", " \
                              + str(inline_response["published-print"]["date-parts"][0][0]) + ")."

            if len(authors) == 2:
                inline_item = " (" + authors[0]["family"] + " & " + authors[1]["family"] + ", " \
                              + str(inline_response["published-print"]["date-parts"][0][0]) + ")."

            if len(authors) > 2:
                inline_item = " (" + authors[0]["family"] + " et al., " \
                              + str(inline_response["published-print"]["date-parts"][0][0]) + ")."

        return inline_item, bib_item

    if identifier_type == "arxiv ID":
        # request_url = "http://export.arxiv.org/api/query?id_list=" + identifier
        # response = urllib.request.urlopen(request_url)
        # dictionary = xmltodict.parse(response.read())

        # title = dictionary["feed"]["entry"]["title"]
        title = "(arXiv reference - work in progress)"

        return title

    return None
