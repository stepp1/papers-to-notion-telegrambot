import json
import logging
import os
import re
from datetime import date

from dotenv import load_dotenv

from src.notion_database.database import Database
from src.notion_database.page import Page
from src.notion_database.properties import Properties


class NotionUpdater:
    """Update Notion Database with new papers."""

    PAGE_TITLE_MAX_LENGTH = 100

    def __init__(self) -> None:
        self.use_ids = True
        self.setup_settings()

    def setup_settings(self) -> None:
        """Setup the settings from the .env file"""

        load_dotenv()
        self.ids_str = "_IDS" if self.use_ids else ""
        self.api_key: str = os.getenv(f"NOTION_API_KEY{self.ids_str}")
        self.page_url: str = os.getenv(f"NOTION_PAGE_URL{self.ids_str}")
        self.database_id: str = self.get_page_id_from_url(self.page_url)

        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)

        self.database = Database(integrations_token=os.getenv("NOTION_API_KEY"))

    def update(self, props_dict: dict[str, str], added_by: str) -> bool:
        """Update a notion page with a dictionary of properties

        Args:
            props_dict (dict): a dictionary of properties
        Returns:
            bool: True if the update was successful
        """
        props = self.generate_notion_properties(props_dict, added_by=added_by)
        P = Page(integrations_token=self.api_key)
        P.create_page(database_id=self.database_id, properties=props, children=None)
        return P

    def generate_notion_properties(self, props_dict, added_by) -> Properties:
        """Generate a notion properties object from a dictionary

        Args:
            props_dict (dict): a dictionary of properties
        Returns:
            props: a notion properties object
        """

        title = (
            props_dict["title"]
            if len(props_dict["title"]) < self.PAGE_TITLE_MAX_LENGTH
            else props_dict["title"][: self.PAGE_TITLE_MAX_LENGTH] + "..."
        )

        authors = props_dict["authors"].split(", ")

        abstract = props_dict["abstract"].strip().replace("\n", " ")
        pub_date = props_dict["date"]
        url = props_dict["url"]
        doi = props_dict["doi"]

        props = Properties()
        props.set_select("Type", "Papers")
        props.set_title("Name", title)
        props.set_multi_select("Authors", authors)
        props.set_url("Link", url)
        props.set_rich_text("Publication Date", pub_date)
        props.set_rich_text("Abstract", abstract)
        props.set_rich_text("Added By", added_by)
        props.set_rich_text("Date Added", date.today().strftime("%Y-%m-%d"))

        return props

    def get_page_id_from_url(self, url: str) -> str:
        """Get the page id from the url

        Args:
            url (str): an url of a notion page

        Returns:
            str: an id from the url
        """
        id_regex = re.compile(r"([\w|\d]{32}$)")
        id_raw = id_regex.findall(url)[0]
        id_processed = "-".join(
            [id_raw[0:8], id_raw[8:12], id_raw[12:16], id_raw[16:20], id_raw[20:]]
        )
        return id_processed
