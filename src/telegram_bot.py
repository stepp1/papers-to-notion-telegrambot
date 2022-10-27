#!/usr/bin/env python
"""
Telegram Bot that saves papers to a Notion Database
It works by extracting a paper's site metadata.

@author: @steppf
"""
import logging
import os
from re import I
from typing import Dict

from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.constants import MessageEntityType
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.notion_updater import NotionUpdater
from src.parser import get_paper_props
from src.utils.parser_utils import extract_urls

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def save_paper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save Paper to Notion."""
    logger.info("Saving paper to notion")
    urls = extract_urls(update.message)
    logger.info(f"Found urls: {urls}")

    paper_props_list = []
    for url in urls:
        try:
            paper_props = get_paper_props(url, logger=logger)

        except Exception as e:
            logger.error(e)
            await update.message.reply_text(f"Error while extracting! {e}")
            return None

        paper_props_list.append(paper_props)

    for paper_props in paper_props_list:
        updater = NotionUpdater()
        update_response = updater.update(
            paper_props, added_by=update.message.from_user.first_name
        )

        database_url = "https://www.notion.so/"
        database_url = (
            database_url
            + update_response.result["parent"]["database_id"]
            + "?v=24bd580ba8164a619bff279cb7decf46"  ## Notion Version??
        )

        logger.info(f"Saved to notion: {database_url}")

        page_url = update_response.result["url"]
        logger.info(f"Notion Page URL: {page_url}")

        title, authors, date, citation_url, abstract = (
            paper_props["title"],
            paper_props["authors"],
            paper_props["date"],
            paper_props["url"],
            paper_props["abstract"].strip().replace("\n", " "),
        )

        await update.message.reply_html(
            f"<b>Saved Paper🎉!</b> \n<b>{title}</b> \nAuthors: {authors}\nDate: {date}\nURL: {citation_url} \n\nNotion Database: {database_url} \nNotion Page: {page_url}."
        )

    return None


def main() -> None:
    """Start the bot."""
    load_dotenv()
    TOKEN = os.environ.get("BOT_TOKEN")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non url messages - check if arvix
    maybe_has_embedded_url = filters.TEXT & (
        filters.Entity(MessageEntityType.URL)
        | filters.Entity(MessageEntityType.TEXT_LINK)
    )

    application.add_handler(
        MessageHandler(
            maybe_has_embedded_url,
            save_paper,
        )
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
