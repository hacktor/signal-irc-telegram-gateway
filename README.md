# Hermod Signal - IRC - Telegram Gateway

[Hermod, or Hermóðr](https://en.wikipedia.org/wiki/Herm%C3%B3%C3%B0r) is a figure in Norse mythology,
often considered the messenger of the gods

These scripts act as a gateway between a telegram group a signal group and an irc channel.
The first thing to do is to register a telegram bot with the **botfather**.
Then you can add the bot to the admins of the telegram channel you want to share with IRC. 
Note the telegram API token and find the telegram group chat\_id.

Reference: [Telegram Bot API](https://core.telegram.org/bots/api "Bot API")

## Configuration

Make a copy of the file hermod.json.example to /etc/hermod.json and change values
appropriately
```json
{       
    "common": {
        "errorsend": "/home/hermod/bin/notify.pl"
    },
    "signal": {
        "phone": "+316xxxxxxxxxx",
        "gid": "XXXXXXXXXXXXXXXXXXXXX==",
        "cli": "/home/hermod/bin/signal-cli",
        "infile": "/home/hermod/log/tosignal.log",
        "db": "/home/hermod/var/signal.db",
        "debug": "/home/hermod/log/signal.debug",
        "anon": "Anonymous",
        "attachments": "/var/www/html/signal",
        "url": "https://hermod.example.com/signal"
    },  
    "telegram": {
        "token":  "999999999:xxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx",
        "chat_id": "-19999999",
        "forward": 1,
        "debug": "/home/hermod/log/telegram.debug",
        "attachments": "/var/www/html/telegram",
        "url": "https://hermod.example.com/telegram"
    },  
    "irc": {
        "node": "irc.freenode.net",
        "channel": "#channel",
        "nick": "gateway",
        "password": "xxxxxxxx",
        "ident": "hermod",
        "ircname": "Hermod Gateway",
        "port": 6697,
        "UseSSL": 1,
        "maxmsg": 400,
        "infile": "/var/www/log/toirc.log",
        "debug": "/var/www/log/irc.debug"
    },
    "twitter": {
        "consumer_key": "xxxxxxxxxxxxxxxxxxxx",
        "consumer_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "token": "xxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxx",
        "token_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "screen_names": [],
        "tags": [],
        "tick": 300
    }
    "matrix": {
        "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "room": "!xxxxxxxxxxxxxxxxxx:matrix.org",
        "bot": "@gateway:matrix.org",
        "debug": "/var/www/log/matrix.debug",
        "infile": "/var/www/log/tomatrix.log",
        "syncurl": "https://matrix.org/_matrix/client/r0/sync?since=__SINCE__&access_token=__TOKEN__",
        "posturl": "https://matrix.org/_matrix/client/r0/rooms/__ROOM__/send/m.room.message?access_token=__TOKEN__",
        "since": "s1371516656_757269739_2333033_498970033_329640559_1201381_52875555_50274419_99428"
    }
}
```
For more detailed information on the various configuration options, consult the [Wiki](./wiki)

**signal-\>phone** is the phone number used by signal-cli. It has to be added to the group (**signal-\>gid**). **signal-\>anon** is a string used to partly anonymize telephone numbers when relaying messages to the other channels. Then the phone number has to be registered with **signal-cli**

Refer to the [Telegram Bot API](https://core.telegram.org/bots/api) for details about **telegram-\>token** and **telegram-\>chat\_id**

**irc-\>node**, **irc-\>channel**, **irc-\>port**, **irc-\>nick** and **irc-\>password** relate to... IRC. Any value for **irc-\>UseSSL** other than 0 will cause the connection to be SSL enabled. Setting **irc-\>maxmsg** will break messages from telegram into chunks of **maxmsg** size.

**irc-\>infile** is the connection between the telegram webhook, the signalpoller and the IRC bot. Can be any file, as long as it is writeable by the webhook and signalpoller and readable by the bot.

The IRC bot and the webhook write to **signal-\>infile**. The poller will read it and send new content to the signal group

## Setting up the hook

The gateway consists of three parts: two daemon parts and a webhook. Place the
webhook in an executable place of a webserver (like **https://webserver/cgi-bin/telegramhook**)

Next thing is to register the webhook:

```bash
curl -F "url=https://webserver/cgi-bin/telegramhook" https://api.telegram.org/bot$TOKEN/setWebhook
```

Make sure the telegram bot you are using has privacy mode disabled. If not, the bot won't see any group messages by other users. You can review the **telegram-\>debug** file to get the chat\_id of the telegram group.

## Setting up Signal

To connect with Signal, you'll need to install [signal-cli](https://github.com/AsamK/signal-cli)

To register the signal phone number you need to run these commands:
```bash
$ signal-cli -u +316xxxxxxxxxx register
$ signal-cli -u +316xxxxxxxxxx verify XXX-XXX
```
The XXX-XXX code you wil get in an SMS text message so you'll have to actually install the simcard in some telephone. This is the only time it's needed.

Set **signal**->**phone** to the number you just registered with **signal-cli**
Next is to add the phone number into a signal group. You can then start **signalpoller** and 
look at its output; when something is said in the signal group you will see output like this:

```text
{"envelope":{"source":"+316xxxxxxxx","sourceDevice":1,"relay":null,"timestamp":1566735523785,"isReceipt":false,"dataMessage":{"timestamp":1566735523785,"message":"Hello","expiresInSeconds":3600,"attachments":[],"groupInfo":{"groupId":"XXXXXXXXXXXXXXXXXXXXXX==","members":null,"name":null,"type":"DELIVER"}},"syncMessage":null,"callMessage":null}}
```
Update **signal**->**gid** in hermod.json  with the **groupId** in this output.

The signal poller does not see usernames, only telephone numbers. It would be kind of rude to relay these telephone numbers to Telegram or IRC, so the telephone numbers are anonymized as "Anonymous-XXXX", where XXXX are the last 4 numbers of the telephone number.

The bot keeps a small sqlite database **signal**->**db**, used for mapping signal telephone numbers (in the signal group) to nicknames. Members of the signal group can set their nick by issuing the command:
```text
!setnick nickname
```
In the signal group. The bot will update the mapping in the database and confirm this by saying:
```text
anonymous-XXXX is now known as nickname
```
In all channels.

You need to create an sqlite database file:
```sql
sqlite> CREATE TABLE alias (phone text unique not null, nick text);
```

## Directories for attachments and urls

The photo's and attachments send by people in telegram and signal groups are downloaded and placed in suitable directories. For Telegram, use the **telegram-\>attachments** configuration option. Make sure this directory is shared over a HTTP webserver like apache and it is writeable by the webserver. Configure **telegram-\>url** to point to this same directory.

The **signal-cli** program by default saves all attachments in a directory **~/.local/share/signal-cli/attachments**. The easiest way to handle this is to move this entire directory to somewhere below the documentroot of the webserver and symlink it.

## following twitter accounts

It is possible to follow twitter accounts. New statuses of these accounts will be posted by the bot. For this functionality you have to setup a [Twitter App](https://developer.twitter.com/en/apps). Fill in the **consumer\_key**, **consumer\_secret**, **token** and **token\_secret** from the app in /etc/hermod.json as well as a list of **screen\_names** you want to follow.

The **twitterpoller** script polls twitter for **screen\_names** and **tags**, relaying newly found statusses. It is possible to skip statuses that are retweets or reply by defining either **twitter-\>noretweet** or **twitter-\>noreply** in hermod.json.

You also need to create an sqlite database for twitter statuses, to weed out double (re)tweets
```sql
sqlite> CREATE TABLE status (id TEXT, ts DATE DEFAULT (datetime('now','localtime')));
sqlite> CREATE UNIQUE INDEX status_id_idx ON status (id);
```
Make sure this database file is writeable by the webserver user.

## Start the IRC bot

Verify permissions on the **signal-\>infile** and **irc-\>infile** files. Both should be writable by the user running the scripts and also by the webserver that is executing the telegram webHook. Then you can start the bot.

```bash
$ ./hermod
Establishing connection to [irc.freenode.net]
:weber.freenode.net NOTICE * :*** Looking up your hostname...
:weber.freenode.net NOTICE * :*** Checking Ident
:weber.freenode.net NOTICE * :*** Couldn't look up your hostname
:weber.freenode.net NOTICE * :*** No Ident response
:weber.freenode.net 001 telegram_gateway :Welcome to the freenode Internet Relay Chat Network telegram_gateway
...
...

```
that's all. You will see messages scrolling showing the login proces on IRC.

## Start the matrixpoller (optional)

You probably want to run these in screen(1) from cron
```bash
@reboot screen -S hermod -d -m while true; do /home/hermod/bin/hermod; done
@reboot screen -S signal -d -m while true; do /home/hermod/bin/signalpoller; done
@reboot screen -S twitter -d -m while true; do /home/hermod/bin/twitterpoller; done
@reboot screen -S matrix -d -m while true; do /home/hermod/bin/matrixpoller; done
```
