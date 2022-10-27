import re


class Config:
    """
    Config for ACM using Dublin Core metadata
    https://www.dublincore.org/specifications/dublin-core/dces/1998-09-01/
    """

    def __init__(self, url):
        self.headers = {
            "Cookie": "MAID=O3g91hsDB/5tHd6ScOA3jQ==; MACHINE_LAST_SEEN=2022-10-27T15%3A23%3A55.204-07%3A00; JSESSIONID=ebc96c0b-6b4f-4635-aa9b-b5cd729c0517; SERVER=WZ6myaEXBLHH8yMKGHbVsw==; __cf_bm=h_aXNGAwHBEPAHCuMMORgEyzfRx3ZVrB6HTbmEsFP7k-1666909435-0-AZ2ys15Y4RF9055ACN6MiMWeP/9qCIjURBbWdRK4q32+IpETcvOjWGcIT9Ujo8/bUrbAKWR0qJnEIwtZvxQkH2Y="
        }

        self.meta = {
            "title": "dc.Title",
            "author": "dc.Creator",
            "date": "dc.Date",
            "url": url.replace("https://dl.acm.org/doi", "https://dl.acm.org/doi/pdf/"),
            "doi": "dc.Identifier",
            "abstract": "Description",
        }

    def parse_author(self, author):
        """
        Parse author string into a tuple of (first name, last name)

        ACM uses the following format:
            LastnameFirstname

        We use the following format:
            "Firstname, Lastname"
        """
        author = re.findall("[a-zA-Z][^A-Z]*", author)
        return f"{author[0]}, {author[1]}"
