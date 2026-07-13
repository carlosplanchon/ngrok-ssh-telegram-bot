# ngrok SSH Telegram Bot

[![CI](https://github.com/carlosplanchon/ngrok-ssh-telegram-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/carlosplanchon/ngrok-ssh-telegram-bot/actions/workflows/ci.yml)

A Python tool that automatically creates secure SSH tunnels using ngrok and sends connection details via Telegram bot notifications.

![Bot Screenshot](assets/ngrok_ssh_telegram_bot_screenshot_20_jul_2025.jpg)

## Overview

Ever needed SSH access to your development machine while away, only to find it's behind NAT or a restrictive firewall? This tool solves that problem by combining ngrok tunneling with Telegram bot notifications for secure, temporary remote access.

## Features

- **Async Architecture**: Built with Python's `trio` library for concurrent operations
- **Secure Authorization**: Only pre-authorized Telegram users receive connection details  
- **Automatic Tunnel Management**: Handles ngrok tunnel creation and monitoring
- **On-demand Access Info**: Message the bot `ip` and it replies with the current connection details
- **Robust Error Handling**: Automatic retry logic for reliable connections

## Architecture

```
┌─────────────────┐    ┌─────────────┐    ┌─────────────────┐
│  Local Machine  │───▶│    ngrok    │───▶│  Public Access  │
│   (SSH on :22)  │    │   Tunnel    │    │   tcp://...     │
└─────────────────┘    └─────────────┘    └─────────────────┘
         │                                          │
         ▼                                          │
┌─────────────────┐                                 │
│ Telegram Bot    │◀────────────────────────────────┘
│ (Authorized     │
│  Users Only)    │
└─────────────────┘
```

## Quick Start

### Prerequisites

1. An SSH server listening on port 22
2. Install ngrok: `sudo snap install ngrok`
3. Install [uv](https://docs.astral.sh/uv/)
4. Get an [ngrok auth token](https://dashboard.ngrok.com/get-started/your-authtoken)
5. Create a Telegram bot via [@BotFather](https://t.me/botfather)
6. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

### Installation

1. Clone this repository
2. Install dependencies: `uv sync`
3. Configure the required JSON files (see Configuration section)

### Configuration

Create these three JSON files in the project root:

#### `ngrok_authtoken.json`
```json
{
  "ngrok_authtoken": "your_ngrok_authtoken_here"
}
```

#### `bot_token.json`
```json
{
  "bot_token": "your_telegram_bot_token_here"
}
```

#### `users.json`
```json
{
  "allowed": {
    "user1": 123456789,
    "user2": 987654321,
    "colleague": 456789123
  }
}
```

**Note**: User IDs are numeric values, not usernames. The keys are just labels for your reference.

### Usage

1. Start the launcher:
   ```bash
   uv run launcher.py
   ```

2. The tool will:
   - Launch ngrok tunnel to localhost:22
   - Poll ngrok API for connection details
   - Start the Telegram bot, which serves the connection details to authorized users

3. Message your bot with `ip` to get connection details.

### Running Tests

```bash
uv run pytest
```

## Security Considerations

### ✅ What's Secure
- **User Authorization**: Only pre-defined Telegram users get access info
- **Temporary Tunnels**: ngrok tunnels are ephemeral
- **No Permanent Exposure**: SSH isn't permanently exposed to internet
- **Encrypted Transport**: the SSH protocol itself encrypts the session end-to-end

### ⚠️ Security Notes
- Use strong SSH key authentication
- Consider IP whitelisting for additional security

## Use Cases

- **Remote Development**: Access your dev machine from anywhere
- **Temporary Collaboration**: Give colleagues temporary SSH access
- **Debugging**: Quick access to staging environments
- **IoT Device Management**: Access devices behind NAT
- **Conference Demos**: Share access during presentations

## How It Works

The tool uses async Python with `trio` to run two concurrent tasks:

1. **Launch ngrok process and monitor tunnel**: Creates secure tunnel to localhost:22
2. **Launch Telegram Bot**: Launch Telegram bot to serve connection details through it.

Once the tunnel is established, authorized users can message the bot `ip` to receive the current connection details.

## Extending the Tool

The modular design makes it easy to extend for:
- Multiple services (HTTP, databases, etc.)
- Different notification channels (Discord, Slack, email)
- Access logging and monitoring
- Auto-expiration features

## License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for more details.

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to fix a bug, feel free to open an issue or submit a pull request.

**To contribute:**

1. Fork this repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a pull request.

Please make sure your code follows the existing style and includes tests if relevant.
By contributing, you agree that your contributions will be licensed under the MIT License.
