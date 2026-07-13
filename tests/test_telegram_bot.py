import json

from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
import trio

from typer.testing import CliRunner

import telegram_bot


ALLOWED_ID = 111111111
OTHER_ALLOWED_ID = 222222222
INTRUDER_ID = 999999999

RESPONSE_TEXT = "0.tcp.sa.ngrok.io:12345"


@pytest.fixture
def config_files(tmp_path, monkeypatch):
    """
    Create users.json and bot_token.json in an isolated temp dir and
    chdir into it, so tests never touch the real config files.
    """
    users = {"allowed": {"andrei": ALLOWED_ID, "backup": OTHER_ALLOWED_ID}}
    (tmp_path / "users.json").write_text(json.dumps(users))

    token = {"bot_token": "123456:TEST-TOKEN"}
    (tmp_path / "bot_token.json").write_text(json.dumps(token))

    monkeypatch.chdir(tmp_path)


def make_update(chat_id: int, text: str) -> MagicMock:
    """
    Build a mock telegram.Update exposing the two things send_resp
    uses: to_dict() and message.reply_text().
    """
    update = MagicMock()
    update.to_dict.return_value = {
        "message": {"chat": {"id": chat_id}, "text": text}
    }
    update.message.reply_text = AsyncMock()
    return update


def make_bot(verbose: bool = False) -> "telegram_bot.TelegramGetBotIp":
    bot = telegram_bot.TelegramGetBotIp(verbose=verbose)
    bot.set_response(RESPONSE_TEXT)
    return bot


class TestConfigLoading:
    def test_get_allowed_users_ids(self, config_files):
        ids = telegram_bot.get_allowed_users_ids()
        assert ids == [ALLOWED_ID, OTHER_ALLOWED_ID]

    def test_allowed_users_ids_are_ints(self, config_files):
        # Telegram sends chat ids as ints: storing them as strings in
        # users.json would silently deny every user.
        ids = telegram_bot.get_allowed_users_ids()
        assert all(isinstance(user_id, int) for user_id in ids)

    def test_get_bot_token(self, config_files):
        assert telegram_bot.get_bot_token() == "123456:TEST-TOKEN"


class TestUpdateHelpers:
    UPDATE_DICT = {"message": {"chat": {"id": 42}, "text": "hola"}}

    def test_get_sender_id(self):
        assert telegram_bot.get_sender_id(update=self.UPDATE_DICT) == 42

    def test_get_message_text(self):
        assert telegram_bot.get_message_text(update=self.UPDATE_DICT) == "hola"


class TestSendResp:
    @pytest.mark.parametrize("text", ["ip", "IP", "Ip", " ip ", "ip "])
    def test_allowed_user_asking_ip_gets_response(self, config_files, text):
        bot = make_bot()
        update = make_update(chat_id=ALLOWED_ID, text=text)

        trio.run(bot.send_resp, update, None)

        update.message.reply_text.assert_awaited_once_with(RESPONSE_TEXT)

    @pytest.mark.parametrize("text", ["hola", "ipconfig", "give me the ip"])
    def test_allowed_user_other_text_gets_no_response(self, config_files, text):
        bot = make_bot()
        update = make_update(chat_id=ALLOWED_ID, text=text)

        trio.run(bot.send_resp, update, None)

        update.message.reply_text.assert_not_awaited()

    def test_unknown_user_gets_no_response(self, config_files):
        bot = make_bot()
        update = make_update(chat_id=INTRUDER_ID, text="ip")

        trio.run(bot.send_resp, update, None)

        update.message.reply_text.assert_not_awaited()

    def test_unknown_user_is_logged_when_verbose(self, config_files, capsys):
        bot = make_bot(verbose=True)
        update = make_update(chat_id=INTRUDER_ID, text="ip")

        trio.run(bot.send_resp, update, None)

        update.message.reply_text.assert_not_awaited()
        assert f"Sender not allowed: {INTRUDER_ID}" in capsys.readouterr().out


class TestCli:
    def test_run_bot_wires_arguments_and_starts(self, monkeypatch):
        bot = MagicMock()
        bot_cls = MagicMock(return_value=bot)
        monkeypatch.setattr(telegram_bot, "TelegramGetBotIp", bot_cls)

        runner = CliRunner()
        result = runner.invoke(telegram_bot.app, ["false", RESPONSE_TEXT])

        assert result.exit_code == 0
        bot_cls.assert_called_once_with(verbose=False)
        bot.set_response.assert_called_once_with(RESPONSE_TEXT)
        bot.start.assert_called_once()
