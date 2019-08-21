# Hermod IRC - Telegram Gateway

[Hermod, or Hermóðr](https://en.wikipedia.org/wiki/Herm%C3%B3%C3%B0r) is a figure in Norse mythology,
often considered the messenger of the gods

These scripts act as a gateway between a telegram group and irc channel.
The first thing to do is to register a telegram bot with the botfather.
Then you can add the bot to the telegram channel you want to share with IRC.
Note the telegram API token and find the telegram group chat\_id.

Reference: [Telegram Bot API](https://core.telegram.org/bots/api "Bot API")

## Configuration

Make a copy of the file hermod.json.example to /etc/hermod.json and change values
appropriately
```json
{
  "token":  "999999999:xxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx",
  "chat_id": "-19999999",
  "group"  : "mygroup",

  "ircnode": "irc.freenode.net",
  "channel": "#channel",
  "port"   : 6697,
  "UseSSL" : 1,
  "nick"   : "telegram_gateway",
  "password": "xxxxxxxx",

  "logfile": "/var/www/log/telegram.log"
}
```
token, chat\_id and group relate to telegram. Refer to the [Telegram Bot API](https://core.telegram.org/bots/api)
for details. 

ircnode, channel, port, nick and password relate to... IRC. Any value for UseSSL other than 0 will cause the connection to be SSL enabled.

logfile is the connection between the telegram webhook and the IRC bot. Can be any file, as long as it is writeable by the webhook and readable by the bot.

## Setting up the hook

The gateway consists of two parts: a daemon part and a webhook. Place the
webhook in an executable place of a webserver (like **https://webserver/cgi-bin/telegramhook**)

Next thing is to register the webhook:

```bash
curl -F "url=https://webserver/cgi-bin/telegramhook" https://api.telegram.org/bot$TOKEN/setWebhook
```

Make sure the telegram bot you are using has privacy mode disabled (or is admin in the telegram group). If not, the bot won't see any group messages by other users.

## Start the IRC bot

Verify the bot is receiving messages in the telegram group by checking the logfile. Then you can start the IRC part:

```bash
$ python hermod.py 
Establishing connection to [irc.freenode.net]
:weber.freenode.net NOTICE * :*** Looking up your hostname...
:weber.freenode.net NOTICE * :*** Checking Ident
:weber.freenode.net NOTICE * :*** Couldn't look up your hostname
:weber.freenode.net NOTICE * :*** No Ident response
:weber.freenode.net 001 telegram_gateway :Welcome to the freenode Internet Relay Chat Network telegram_gateway
...
...

```
that's all. You will see messages scrolling showing the login proces on IRC. You probably want to run this in screen(1) from cron
```bash
@reboot screen -d -m python /home/hacktor/bin/hermod.py
```


