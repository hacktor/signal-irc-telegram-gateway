#!/usr/bin/python
# IRC Bot for Hermod Telegram and Signal Gateway. Works with sigpoller for receiving
# messages from a signal group and telegramhook for a telegram group.
# configuration in /etc/hermod.json
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
import subprocess

## Settings
with open('/etc/hermod.json') as f:
    config = json.load(f)

irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
if config['UseSSL'] != 0:
    irc = ssl.wrap_socket(irc_C)
else:
    irc = irc_C

print "Establishing connection to [%s]" % (config['ircnode'])
# Connect to IRC channel
irc.connect((config['ircnode'], config['port']))
irc.setblocking(False)
irc.send("PASS %s\n" % (config['password']))
irc.send("USER "+ config['nick'] +" "+ config['nick'] +" "+ config['nick'] +" :herMod-Test\n")
irc.send("NICK "+ config['nick'] +"\n")
irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (config['nick'], config['password']))
irc.send("JOIN "+ config['channel'] +"\n")


firstcall = True
f = open(config['sigfile'], 'r')
g = open(config['telfile'], 'r')

while True:
    time.sleep(1)
    URL = "https://api.telegram.org/bot" + config['token'] + "/sendMessage?chat_id=" + config['chat_id'] + "&text="

    # Tail log Files, forward lines to IRC
    try:
        if firstcall:
            f.seek(0,2)
            g.seek(0,2)
            firstcall = False

        sigline = f.readline()
        telline = g.readline()
        if sigline != '':
            irc.send("PRIVMSG %s :%s" % (config['channel'], sigline))
            print "Send to IRC: " + sigline
        if telline != '':
            irc.send("PRIVMSG %s :%s" % (config['channel'], telline))
            print "Send to IRC: " + telline
    except Exception as e:
        print e

    # Read new IRC messages, forward lines to Signal and Telegram
    try:
        buf = irc.recv(2040)
        
        texts = buf.splitlines()
        for text in texts:
            print text
            URL = "https://api.telegram.org/bot" + config['token'] + "/sendMessage?chat_id=" + config['chat_id'] + "&text="

            if text.find('PRIVMSG ' + config['channel']) != -1:
                nick = text.partition('!')[0].strip(':')
                msg = text.rpartition('PRIVMSG ' + config['channel'] + ' :')[2]
                if msg[1:7] == 'ACTION':
                    msg = "[IRC] ***" + nick + " " + msg.rpartition('ACTION')[2]
                else:
                    msg = "[IRC " + nick + "]: " + msg

                # Send to Telegram
                requests.get(URL + urllib.quote(msg))

                # Send to Signal
                h = open(config['tosignal'], "a")
                h.write(msg)
                h.write("\n")
                h.close()

                print "Send to Signal and Telegram: " + msg

            # Prevent Timeout
            if text.find('PING') != -1:
                irc.send('PONG ' + text.split() [1] + '\r\n')
    except Exception:
        continue
