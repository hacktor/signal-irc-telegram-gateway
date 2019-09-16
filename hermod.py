#!/usr/bin/python2
# IRC Bot for Hermod Telegram and Signal Gateway. Works with sigpoller for receiving
# messages from a signal group and telegramhook for a telegram group.
# configuration in /etc/hermod.json
#
# 2019, Ruben de Groot
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
    cfg = json.load(f)

irc_C = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
if cfg['irc']['UseSSL'] != 0:
    irc = ssl.wrap_socket(irc_C)
else:
    irc = irc_C

print "Establishing connection to [%s]" % (cfg['irc']['node'])
# Connect to IRC channel
irc.connect((cfg['irc']['node'], cfg['irc']['port']))
irc.setblocking(False)
irc.send("PASS %s\n" % (cfg['irc']['password']))
irc.send("USER "+ cfg['irc']['nick'] +" "+ cfg['irc']['nick'] +" "+ cfg['irc']['nick'] +" :herMod-Test\n")
irc.send("NICK "+ cfg['irc']['nick'] +"\n")
irc.send("PRIVMSG nickserv :identify %s %s\r\n" % (cfg['irc']['nick'], cfg['irc']['password']))
irc.send("JOIN "+ cfg['irc']['channel'] +"\n")


firstcall = True
f = open(cfg['signal']['file'], 'r')
g = open(cfg['telegram']['file'], 'r')

while True:
    time.sleep(1)
    URL = "https://api.telegram.org/bot" + cfg['telegram']['token'] + "/sendMessage?chat_id=" + cfg['telegram']['chat_id'] + "&text="

    # Tail log Files, forward lines to IRC
    try:
        if firstcall:
            f.seek(0,2)
            g.seek(0,2)
            firstcall = False

        sigline = f.readline()
        telline = g.readline()
        if sigline != '':
            irc.send("PRIVMSG %s :%s" % (cfg['irc']['channel'], sigline))
            print "Send to IRC: " + sigline
        if telline != '':
            irc.send("PRIVMSG %s :%s" % (cfg['irc']['channel'], telline))
            print "Send to IRC: " + telline
    except Exception as e:
        print e

    # Read new IRC messages, forward lines to Signal and Telegram
    try:
        buf = irc.recv(2040)
        
        texts = buf.splitlines()
        for text in texts:
            print text
            URL = "https://api.telegram.org/bot" + cfg['telegram']['token'] + "/sendMessage?chat_id=" + cfg['telegram']['chat_id'] + "&text="

            if text.find('PRIVMSG ' + cfg['irc']['channel']) != -1:
                nick = text.partition('!')[0].strip(':')
                msg = text.rpartition('PRIVMSG ' + cfg['irc']['channel'] + ' :')[2]
                if msg[1:7] == 'ACTION':
                    msg = "[IRC] ***" + nick + " " + msg.rpartition('ACTION')[2]
                else:
                    msg = "[IRC " + nick + "]: " + msg

                # Send to Telegram
                requests.get(URL + urllib.quote(msg))

                # Send to Signal
                h = open(cfg['signal']['infile'], "a")
                h.write(msg)
                h.write("\n")
                h.close()

                print "Send to Signal and Telegram: " + msg

            # Prevent Timeout
            if text.find('PING') != -1:
                irc.send('PONG ' + text.split() [1] + '\r\n')
    except Exception:
        continue
