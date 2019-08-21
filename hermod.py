#!/usr/bin/python
# IRC Bot for Hermod Telegram Gateway. Works with telegramhook for receiving
# messages from a telegram group.
#
# 2019-08-17, Ruben de Groot
#
# This is the python version of what started as a perl project.

import socket
import ssl
import time
import requests
import urllib
import json

## Settings
with open('/etc/hermod.json') as f:
    config = json.load(f)

irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
if config['UseSSL'] != 0:
    irc = ssl.wrap_socket(irc_C)
else:
    irc = irc_C

print "Establishing connection to [%s]" % (config['ircnode'])
# Connect
irc.connect((config['ircnode'], config['port']))
irc.setblocking(False)
irc.send("PASS %s\n" % (config['password']))
irc.send("USER "+ config['nick'] +" "+ config['nick'] +" "+ config['nick'] +" :herMod-Test\n")
irc.send("NICK "+ config['nick'] +"\n")
irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (config['nick'], config['password']))
irc.send("JOIN "+ config['channel'] +"\n")


firstcall = True
f = open(config['logfile'], 'r')

while True:
    time.sleep(1)

    # Tail File
    try:
        if firstcall:
            f.seek(0,2)
            firstcall = False

        line = f.readline()
        if line != '':
            irc.send("PRIVMSG %s :%s" % (config['channel'], line))
            print "Send to IRC: " + line
    except Exception as e:
        print "Error with file %s" % (config['logfile'])
        print e

    try:
        buf = irc.recv(2040)
        
        texts = buf.splitlines()
        for text in texts:
            print text

            if text.find('PRIVMSG ' + config['channel']) != -1:
                nick = text.partition('!')[0].strip(':')
                msg = "IRC Msg by " + nick + ": " + text.rpartition('PRIVMSG ' + config['channel'] + ' :')[2]
                print "send to telegram: " + msg
                URL = "https://api.telegram.org/bot" + config['token'] + "/sendMessage?chat_id=" + config['chat_id'] + "&text=" + urllib.quote(msg)
                requests.get(URL)

            # Prevent Timeout
            if text.find('PING') != -1:
                irc.send('PONG ' + text.split() [1] + '\r\n')
    except Exception:
        continue
