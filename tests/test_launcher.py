import json

import launcher


class TestParsePublicUrl:
    def test_parses_host_and_port(self):
        host, port = launcher.parse_public_url("tcp://0.tcp.sa.ngrok.io:12345")

        assert host == "0.tcp.sa.ngrok.io"
        assert port == 12345

    def test_host_starting_with_prefix_chars_is_preserved(self):
        # Regression: lstrip("tcp://") used to eat leading t/c/p
        # characters from the host itself.
        host, port = launcher.parse_public_url("tcp://tcp.eu.ngrok.io:80")

        assert host == "tcp.eu.ngrok.io"
        assert port == 80


def test_get_ngrok_authtoken(tmp_path, monkeypatch):
    token = {"ngrok_authtoken": "test-authtoken"}
    (tmp_path / "ngrok_authtoken.json").write_text(json.dumps(token))
    monkeypatch.chdir(tmp_path)

    assert launcher.get_ngrok_authtoken() == "test-authtoken"
