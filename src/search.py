import sys

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from notion_database.query import Direction, Timestamp
from notion_database.request import Request


class SortType(TypedDict):
    direction: Direction
    timestamp: Timestamp


class Search:
    def __init__(self, integrations_token):
        """
        init

        :param integrations_token: Notion Internal Integration Token
        """
        self.properties_list = []
        self.url = 'https://api.notion.com/v1/search'
        self.result = {}
        self.request = Request(self.url, integrations_token=integrations_token)

    def search_database(self, query: str, sort: SortType, root_only=True):
        """
        Searches all original databases and child databases that are shared with the integration

        :param query: matches against the database titles.
        :param sort: sort query specifically for only databases.
        :param root_only: get only the root databases.
        :return:
        """
        self.result = self.request.call_api_post(self.url + "/", {
            "query": query, "sort": {"direction": sort["direction"].value, "timestamp": sort["timestamp"].value},
            "filter": {"value": "database", "property": "object"}
        })["results"]
        root_list = []
        if root_only:
            result = self.result
            for db_index in range(len(result)):
                db = result[db_index]
                if db["parent"].get("workspace", None):
                    root_list.append(db)
            self.result = root_list

    def search_pages(self, query: str, sort: SortType, page_size=100, start_cursor: str = None):
        """
        Searches all original pages and child pages that are shared with the integration

        :param query: matches against the pages titles.
        :param sort: sort query specifically for only pages.
        :param page_size: The number of items from the full list desired in the response.
        :param start_cursor: returns a page of results starting after the cursor provided.
        :return:
        """
        if start_cursor:
            self.result = self.request.call_api_post(self.url + "/", {
                "query": query, "sort": {"direction": sort["direction"].value, "timestamp": sort["timestamp"].value},
                "filter": {"value": "page", "property": "object"}, "page_size": page_size, "start_cursor": start_cursor
            })
        self.result = self.request.call_api_post(self.url + "/", {
            "query": query, "sort": {"direction": sort["direction"].value, "timestamp": sort["timestamp"].value},
            "filter": {"value": "page", "property": "object"}, "page_size": page_size
        })
