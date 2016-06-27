# Simple Push Python Module

import znc
import re
import http.client, urllib
import traceback

def findWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

class pypush(znc.Module):
    module_types = [znc.CModInfo.UserModule]
    description = "Push python3 module for ZNC"

    def OnLoad(self, sArgs, sMessage):
        self.nick = 'rje'
        self.PutModule("Load Test")
        #self.PutModule("Loaded for user: {0}".format(self._cmod.GetUser()))
        self.InitHighlightWords(self.nv['highlight'].split())
        return znc.CONTINUE

    def InitHighlightWords(self, words=None):
        self.words = [self.nick, ]
        try:
            self.words.extend(words)
        except Exception:
            pass
        self.PutModule("Highlight Words: {0}".format(self.words))

    def PushMsg(self, title, msg):
        self.PutModule("{0} -- {1}".format(title, msg))
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": self.nv['token'],
                         "user": self.nv['user'],
                         "title": title,
                         "message": msg,
                     }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

    def OnChanMsg(self, nick, channel, message):
        for word in self.words:
            if findWord(word)(message.s):
                self.PushMsg("Highlight", "{0}: [{1}] {2}".format(channel.GetName(), nick.GetNick(), message.s))
                break
        return znc.CONTINUE

    def OnPrivMsg(self, nick, message):
        self.PushMsg("Private", "[{0}] {1}".format(nick.GetNick(), message.s))
        return znc.CONTINUE

    def OnModCommand(self, commandstr):
        argv = commandstr.split()
        try:
            self.PutModule("Command!! {0}".format(argv))
            method = getattr(self, "DoCommand" + argv[0].replace('-','_'), self.DoCommandNotUnderstood)
            method(argv)
        except Exception:
            self.PutModule("Command Exception!! {0} -> {1}".format(argv, traceback.format_exc()))
        return znc.CONTINUE

    def DoCommandNotUnderstood(self, argv):
        self.PutModule("Command Not Understood: {0}".format(argv))
        
    def DoCommandSetUser(self, argv):
        try:
            self.nv['user'] = argv[1]
            self.PutModule("Pushover user set")
        except Exception:
            self.PutModule("SetUser requires a Pushover user string");

    def DoCommandSetToken(self, argv):
        try:
            self.nv['token'] = argv[1]
            self.PutModule("Pushover token set")
        except Exception:
            self.PutModule("SetToken requires a Pushover token string");

    def DoCommandSetHighlight(self, argv):
        self.nv['highlight'] = ' '.join(argv[1:])
        self.InitHighlightWords(argv[1:])

