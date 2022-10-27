import re


class Config:
    def __init__(self, url):
        self.headers = {"Cookie": ""}

        self.meta = {
            "title": "citation_title",
            "author": "citation_author",
            "date": re.compile(r"^citation(.*)date"),
            "url": re.compile(r"^citation(.*)url"),
            "doi": "citation_arxiv_id",
            "abstract": re.compile(r"(?:citation_abstract|description)"),
        }

    def parse_author(self, author):
        """
        Parse author string into a string of "first name, last name"
        """
        return author
