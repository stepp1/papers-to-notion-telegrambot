from db import session, User, create_new_user, check_if_user_exists
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from notion.client import NotionClient
from notion.block import TextBlock

TYPING_NOTION_API_KEY, TYPING_NOTION_PAGE_ADDRESS = range(2)

keyboard = ReplyKeyboardMarkup(
    [["/start", "/help", "/setclient"], ["/check_client", "/setpage", "/check_page"]],
    True,
)


def start(update, context):
    username = update.message.from_user.username

    if not check_if_user_exists(session, username):
        create_new_user(session, username)

    reply_text = f"""Hey there, {username}!
    I\'m a deadpan simple bot for sending text to Notion.
    Use /help to get the instructions. 

    Now, let's set me up for work!
    """
    update.message.reply_text(reply_text, reply_markup=keyboard)
    setup(update, context)
    return ConversationHandler.END


def setup(update, context):
    update.message.reply_text("checking user settings...", reply_markup=keyboard)
    check_client(update, context)
    check_page(update, context)
    return ConversationHandler.END


def help_msg(update, context):
    reply_text = f"""

    1. Create a Notion integration and get an API key by following official Getting Started guide: https://developers.notion.com/docs/getting-started
    2. Create a database that will be used as an Inbox for text sent by the bot and open it for  (for details, see the same Getting Started guide)
    3. Use /setkey command in the bot and send API key
    4. Copy database's page ID (for example, in https://www.notion.so/myusername/91e3466bc884471489f5774587e94bbb the ID would be 91e3466bc884471489f5774587e94bbb)
    5. use /set_inbox_database and send database ID to bot

    Now any text you send to bot (except for commands) will be added as an entry in Inbox database.
    """
    update.message.reply_text(reply_text, reply_markup=keyboard)
    return ConversationHandler.END


def ask_notion_api_key(update, context):
    update.message.reply_text("please send me an Notion API key", reply_markup=keyboard)
    return TYPING_NOTION_API_KEY


def set_notion_api_key(update, context):
    update.message.reply_text("setting Notion API key...", reply_markup=keyboard)

    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    user.notion_api_key = update.message.text

    session.commit()

    update.message.reply_text("✓ Notion API key set.", reply_markup=keyboard)

    setclient(update, context, user)

    return ConversationHandler.END


def setclient(update, context, user):
    update.message.reply_text("setting Inbox database...")
    # update.message.reply_text(f'Your API key is: {user.notion_api_key}')

    try:
        context.user_data["notion_client"] = user.notion_api_key
        update.message.reply_text("✓ Notion client set!", reply_markup=keyboard)
    except Exception as e:
        update.message.reply_text(
            f"☢ Error while setting Notion client: {e}", reply_markup=keyboard
        )

    return ConversationHandler.END


def check_client(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    if user.notion_api_key:
        update.message.reply_text("✓ Notion API key set!", reply_markup=keyboard)

    if not user.notion_api_key:
        update.message.reply_text("☢ Notion API key not set.", reply_markup=keyboard)
        ask_notion_api_key(update, context)

    if context.user_data.get("notion_client"):
        update.message.reply_text("✓ Notion client set!", reply_markup=keyboard)

    if not context.user_data.get("notion_client"):
        update.message.reply_text("☢ Notion client not set.", reply_markup=keyboard)
        setclient(update, context, user)

    return ConversationHandler.END


def askpage(update, context):
    update.message.reply_text(
        "please send me an ID of Notion database", reply_markup=keyboard
    )
    return TYPING_NOTION_PAGE_ADDRESS


def set_database_id(update, context):
    try:
        update.message.reply_text("setting Inbox database...")

        username = update.message.from_user.username
        user = session.query(User).filter(User.username == username).first()

        database_id = update.message.text
        user.page_address = database_id

        session.commit()

        update.message.reply_text(f"Inbox database set to {database_id}.")

    except Exception as e:
        update.message.reply_text(
            f"☢ error while setting Inbox database: {e}", reply_markup=keyboard
        )

    connect_to_page(update, context, user, user.page_address)

    return ConversationHandler.END


def connect_to_page(update, context, user, page_address):
    try:
        update.message.reply_text("setting database...")
        notion_client = context.user_data["notion_client"]
        page = notion_client.get_block(user.page_address)
        context.user_data["page"] = page
        user.page_title = page.title

        session.commit()

        update.message.reply_text(f"✓ connected to database {user.page_title}!")

    except Exception as e:
        update.message.reply_text(
            f"☢ error while connecting to page: {e}", reply_markup=keyboard
        )
    # если это не сделать, он уйдет в бесконечное 'page set to'!
    return ConversationHandler.END


def check_page(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    if user.page_address:
        update.message.reply_text(f"✓ page address set.", reply_markup=keyboard)

    if not user.page_address:
        update.message.reply_text("☢ page address not set.", reply_markup=keyboard)
        askpage(update, context)

    if context.user_data.get("page"):
        update.message.reply_text(
            f"✓ connected to page {user.page_title}.", reply_markup=keyboard
        )

    if not context.user_data.get("page"):
        update.message.reply_text("☢ page not connected.", reply_markup=keyboard)
        connect_to_page(update, context, user, user.page_address)

    return ConversationHandler.END


def send_text_to_notion(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    try:
        text = update.message.text
        page = context.user_data["page"]
        newblock = page.children.add_new(TextBlock, title=text)
        update.message.reply_text(
            f"Sent text to {user.page_title}.", reply_markup=keyboard
        )
    except Exception as e:
        update.message.reply_text(
            f"☢ Error while sending text to Notion: {e}", reply_markup=keyboard
        )

    return ConversationHandler.END


def done(update, context):
    update.message.reply_text("ok then.")
    return ConversationHandler.END
