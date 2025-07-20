#!/usr/bin/env python3

from subprocess import DEVNULL

import httpx
import trio

import json


NGROK_LOCAL_API_URL: str = "http://127.0.0.1:4040/api/tunnels"


def get_ngrok_authtoken() -> str:
    with open("ngrok_authtoken.json", "r") as f:
        token_dict = json.load(f)

    ngrok_authtoken: str = token_dict["ngrok_authtoken"]
    return ngrok_authtoken


async def launch_ngrok_process() -> None:
    print("Launching NGROK...")
    ngrok_authtoken: str = get_ngrok_authtoken()

    # Installed with "snap install ngrok":
    CMD = ["ngrok", "tcp", "22", "--authtoken", ngrok_authtoken]

    await trio.run_process(CMD, stdout=DEVNULL)
    print("Process launched.")
    return None


async def launch_telegram_bot(host: str, port: int):
    resp = f"{host}:{port}"

    CMD = ["python", "telegram_bot.py", "False", resp]

    await trio.run_process(CMD, stdout=DEVNULL)
    print("Bot launched.")


async def get_ngrok_public_address() -> tuple[str, int]:
    print("Getting NGROK public address...")

    connection_successful: bool = False
    while connection_successful is False:
        result = None
        try:
            result = httpx.get(url=NGROK_LOCAL_API_URL)
        except Exception as e:
            print(f"HTTPX Async Client > Exception: {e}")
            ...

        try:
            if result is not None and result.status_code == 200:
                json_resp = result.json()
                print("--- JSON RESP ---")
                public_url: str = json_resp["tunnels"][0]["public_url"]
                public_url = public_url.lstrip("tcp://")

                parts = public_url.split(":")

                host: str = parts[0]
                port: int = int(parts[1])
                connection_successful = True
        except Exception:
            print("...")

        await trio.sleep(0.2)

    print(f"username@{host} -p {port}")

    await launch_telegram_bot(host=host, port=port)


async def main() -> None:
    async with trio.open_nursery() as nursery:
        nursery.start_soon(launch_ngrok_process)
        nursery.start_soon(get_ngrok_public_address)

    return None


if __name__ == "__main__":
    trio.run(main)
