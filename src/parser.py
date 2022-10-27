"""This module contains helper functions.

- Extract URLs from messages.
- Get a paper properties from URL.
- Format Authors.

@author: @steppf
"""

import importlib
import re
from distutils.command.config import config
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.utils.parser_utils import join_authors
from src.utils.request_utils import DefaultSession


class PaperParser:
    """
    Parser that extracts the following properties from a paper html.

    1. We use the BeautifulSoup library to parse the html code of the page that we are interested in.
    2. We extract data from the page using the find() and findAll() methods of the BeautifulSoup class.
    3. Finally, we return the dictionary containing the extracted properties.
    """

    def __init__(self, url: str, logger=None):
        self.url = url
        self.logger = logger
        self.parser = self._get_parser(self.url)
        self.session = DefaultSession(headers=self.parser.headers)
        self.soup = self._get_soup(self.url)

    def _get_parser(self, url: str):
        provider = urlparse(url).netloc.split(".")[-2]
        self.logger.info(f"Provider: {provider}")

        provider_module = f"src.parsers.{provider}"
        provider_module = importlib.import_module(provider_module)

        parser = provider_module.Config(url)
        return parser

    def _get_soup(self, url: str):
        response = self.session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            return soup

        raise ConnectionError(
            f"{url} \nError: {response.status_code}, {response.reason} \nHeaders: {self.session.headers}"
        )

    def _get_title(self):
        title_meta = self.parser.meta["title"]
        title = self.soup.find("meta", attrs={"name": title_meta})
        title = title.get("content").strip()
        return title

    def _get_authors(self):
        author_meta = self.parser.meta["author"]
        authors = [
            self.parser.parse_author(tag.get("content")).strip()
            for tag in self.soup.findAll("meta", attrs={"name": author_meta})
        ]

        return authors

    def _get_date(self):
        date_meta = self.parser.meta["date"]
        date = self.soup.find("meta", attrs={"name": date_meta}).get("content")
        date = date.strip()
        return date

    def _get_url(self):
        # citation url (pdf or other)
        url_meta = self.parser.meta["url"]
        if self.url.startswith("http"):
            citation_url = self.url
        else:
            citation_url = self.soup.find("meta", attrs={"name": url_meta}).get(
                "content"
            )

        citation_url = citation_url.strip()
        return citation_url

    def _get_doi(self):
        doi_meta = self.parser.meta["doi"]
        if doi_meta is None:
            return ""
        doi = self.soup.find("meta", attrs={"name": doi_meta}).get("content")
        doi = doi.strip()
        return doi

    def _get_abstract(self):
        abstract_meta = self.parser.meta["abstract"]
        abstract = self.soup.find(
            "meta",
            attrs={"name": abstract_meta},
        ).get("content")
        abstract = abstract.strip()
        abstract = re.sub(r"'(?:\\n)+", " ", str(abstract))
        abstract = " ".join(abstract.splitlines())
        # TODO: CHECK \n because it's not working
        return abstract

    def extract_props(self):
        self.logger.info("Paper Properties:")

        title = self._get_title()
        self.logger.info(title)

        authors = self._get_authors()
        self.logger.info(authors)

        date = self._get_date()
        self.logger.info(date)

        citation_url = self._get_url()
        self.logger.info(citation_url)

        doi = self._get_doi()
        self.logger.info(doi)

        abstract = self._get_abstract()

        self.paper_props = {
            "title": title,
            "authors": join_authors(authors),
            "date": date,
            "url": citation_url,
            "doi": doi,
            "abstract": abstract,
        }

        return self.paper_props


def get_paper_props(url: str, logger=Optional) -> dict[str, str]:
    """
    Extract and format paper properties from a given URL.

    Args:
        url (str): The URL of the paper.
    Returns:
        dict[str, str]: A dictionary containing the paper properties.
    """
    logger.info(f"Getting paper props for {url}")

    parser = PaperParser(url, logger)
    paper_props = parser.extract_props()
    return paper_props
