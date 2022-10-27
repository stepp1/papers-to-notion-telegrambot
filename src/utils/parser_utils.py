from typing import Dict, List

from telegram import Message, MessageEntity


def extract_urls(message: Message) -> List[str]:
    """
    Extracts all hyperlinks that are contained in a message. This includes message entities and the
    media caption, i.e. while of course only text *or* caption is present this works for both.
    Distinct links are returned in order of appearance.
    Note:
        For exact duplicates, only the first appearance will be kept, but there may still be URLs
        that link to the same resource.
    Args:
        message (:obj:`telegram.Message`): The message to extract from
    Returns:
        :obj:`list`: A list of URLs contained in the message
    """

    types = [MessageEntity.URL, MessageEntity.TEXT_LINK]
    results = message.parse_entities(types=types)
    results.update(message.parse_caption_entities(types=types))

    # Get the actual urls
    for key in results:
        if key.type == MessageEntity.TEXT_LINK:
            results[key] = key.url

    # Remove exact duplicates and keep the first appearance
    filtered_results: Dict[str, MessageEntity] = {}
    for key, value in results.items():
        if not filtered_results.get(value):
            filtered_results[value] = key
        else:
            if key.offset < filtered_results[value].offset:
                filtered_results[value] = key

    # Sort results by order of appearance, i.e. the MessageEntity offset
    sorted_results = sorted(filtered_results.items(), key=lambda e: e[1].offset)

    return [k for k, v in sorted_results]


def format_author(author):
    return " ".join(author.split(", ")[::-1])


def join_authors(authors):
    authors = [format_author(author) for author in authors]
    return ", ".join(authors)
