# irc-telegram-gateway

Scripts acting as a gateway between a telegram group and irc channel.
The first thing to do is to register a telegram bot with the botfather.
Note the telegram API token and find the telegram group chat\_id.

Reference: [Telegram Bot API](https://core.telegram.org/bots/api "Bot API")

## Setting up the hook

The gateway consists of two parts: a daemon part and a webhook. Place the
webhook in an executable place of a webserver (like **https://webserver/cgi-bin/telegramhook**)

Next thing is to register the webhook:

```bash
curl -F "url=https://webserver/cgi-bin/telegramhook" https://api.telegram.org/bot$TOKEN/setWebhook
```

