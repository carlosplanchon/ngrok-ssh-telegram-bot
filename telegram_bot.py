#!/usr/bin/env python3

# ! uv add python-telegram-bot

import json

import logging

import typer

from telegram import Update
from telegram.ext import Application
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from typing import Any

app = typer.Typer()


def get_allowed_users_ids() -> list[str]:
    with open("users.json", "r") as f:
        users_dict = json.load(f)

    active_users_id = list(users_dict["allowed"].values())
    return active_users_id


def get_bot_token() -> str:
    with open("bot_token.json", "r") as f:
        token_dict = json.load(f)

    token = token_dict["bot_token"]
    return token


def get_sender_id(update: dict[Any]) -> int:
    return update["message"]["chat"]["id"]


def get_message_text(update: dict[Any]) -> str:
    return update["message"]["text"]


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
# set higher logging level for httpx
# to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class TelegramGetBotIp:
    def __init__(
        self,
        verbose: bool = False,
            ):
        self.BOT_TOKEN = get_bot_token()
        self.ALLOWED_TELEGRAM_USERS_ID = get_allowed_users_ids()

        self.VERBOSE = verbose

    def set_response(self, resp: str) -> None:
        self.RESPONSE_TEXT: str = resp

    async def send_resp(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
            ) -> None:
        update_dict = update.to_dict()
        sender_id = get_sender_id(update=update_dict)
        print(f"SENDER ID: {sender_id}")

        if sender_id in self.ALLOWED_TELEGRAM_USERS_ID:
            message_text = get_message_text(update=update_dict)
            if self.VERBOSE is True:
                print(f"Sender: {sender_id} sent: {message_text}")

            if message_text.lower().strip(" ") == "ip":
                await update.message.reply_text(self.RESPONSE_TEXT)
        else:
            if self.VERBOSE:
                print(f"Sender not allowed: {sender_id}")

    def start(self) -> None:
        """
        Start bot and keep it running in its own task.
        """
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(self.BOT_TOKEN).build()

        # on non command i.e message - echo the message on Telegram
        application.add_handler(
            MessageHandler(filters.TEXT, self.send_resp)
        )

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


@app.command()
def run_bot(verbose: bool, response: str):
    bot = TelegramGetBotIp(verbose=verbose)
    bot.set_response(response)
    bot.start()


if __name__ == "__main__":
    app()
