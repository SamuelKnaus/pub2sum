import json
import urllib.request
from urllib.error import HTTPError

import pdf2doi


def get_references(file_path):
    information = pdf2doi.pdf2doi(file_path)
    identifier_type = information["identifier_type"]
    identifier = information["identifier"]

    references = fetch_bibliography(identifier_type, identifier)

    if references:
        return references

    return "Could not find reference!"


def fetch_bibliography(identifier_type, identifier):
    if identifier_type == "DOI":
        inline_item = "Could not find reference for " + identifier
        bibliography_item = "Could not find reference for " + identifier
        request_url = "http://dx.doi.org/" + identifier

        bib_request = urllib.request.Request(request_url)
        bib_request.add_header('Accept', 'text/x-bibliography')
        bib_request.add_header('style', 'apa-6th-edition')

        inline_request = urllib.request.Request(request_url)
        inline_request.add_header('Accept', 'application/vnd.citationstyles.csl+json')

        try:
            with urllib.request.urlopen(bib_request) as f:
                bibliography_item = f.read().decode()

            with urllib.request.urlopen(inline_request) as f:
                inline_response = json.loads(f.read().decode())
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
        except HTTPError as e:
            if e.code == 404:
                print('DOI not found.')
            else:
                print('Service unavailable.')

        return inline_item, bibliography_item

    if identifier_type == "arxiv ID":
        # request_url = "http://export.arxiv.org/api/query?id_list=" + identifier
        # response = urllib.request.urlopen(request_url)
        # dictionary = xmltodict.parse(response.read())

        # title = dictionary["feed"]["entry"]["title"]
        title = "arXiv reference - work in progress"

        return title

    return None
