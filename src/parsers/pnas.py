import re


class Config:
    def __init__(self, url):
        self.headers = {
            "Cookie": "MAID=O3g91hsDB/5tHd6ScOA3jQ==; MACHINE_LAST_SEEN=2022-10-27T15%3A23%3A55.204-07%3A00; JSESSIONID=ebc96c0b-6b4f-4635-aa9b-b5cd729c0517; SERVER=WZ6myaEXBLHH8yMKGHbVsw==; __cf_bm=YBYnkrVB7cvAI96Ud1h1d40Z3w_Y4ySz_O3iiLxbu0U-1666911181-0-AbuYZHCj5KYoE2oIHmBpfHHhZypU+yI43TvuYYyjgOmvBlhW3f+VCNmMDJhO8VqPSyzXdV6qNZ4vU7tZu+PeWcs="
            # "Upgrade-Insecure-Requests": 1,
            # "Sec-Fetch-Dest": "document",
            # "Sec-Fetch-Mode": "navigate",
            # "Sec-Fetch-Site": "none",
            # "Sec-Fetch-User": "?1",
            # "Sec-GPC": 1,
            # "TE": "trailers",
        }

        self.meta = {
            "title": "citation_title",
            "author": "citation_author",
            "date": re.compile(r"^citation(.*)date"),
            "url": re.compile(r"^citation(.*)url"),
            "doi": "citation_doi",
            "abstract": re.compile(r"(?:citation_abstract|description)"),
        }

    def parse_author(self, author):
        """
        Parse author string into a string of "first name, last name"
        """
        return author
