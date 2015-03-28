#!/usr/bin/env python

#import sys
#import gtk
#import appindicator
#import imaplib
#import re
#
#PING_FREQUENCY = 5 # seconds
#
#class CheckGMail:
#    def __init__(self):
#        self.ind = appindicator.Indicator("new-gmail-indicator",
#                                           "indicator-messages",
#                                           appindicator.CATEGORY_APPLICATION_STATUS)
#        self.ind.set_status(appindicator.STATUS_ACTIVE)
#        self.ind.set_attention_icon("new-messages-red")
#        self.menu_setup()
#        self.ind.set_menu(self.menu)
#
#    def menu_setup(self):
#        self.menu = gtk.Menu()
#
#        self.quit_item = gtk.MenuItem("Quit")
#        self.quit_item.connect("activate", self.quit)
#        self.quit_item.show()
#        self.menu.append(self.quit_item)
#
#    def main(self):
#        self.check_mail()
#        gtk.timeout_add(PING_FREQUENCY * 1000, self.check_mail)
#        gtk.main()
#
#    def quit(self, widget):
#        sys.exit(0)
#
#    def check_mail(self):
#        #messages, unread = self.gmail_checker('myaddress@gmail.com','mypassword')
#        messages, unread = 0, 3
#        if unread > 0:
#            self.ind.set_status(appindicator.STATUS_ATTENTION)
#        else:
#            self.ind.set_status(appindicator.STATUS_ACTIVE)
#        return True
#
#    def gmail_checker(self, username, password):
#        i = imaplib.IMAP4_SSL('imap.gmail.com')
#        try:
#            i.login(username, password)
#            x, y = i.status('INBOX', '(MESSAGES UNSEEN)')
#            messages = int(re.search('MESSAGES\s+(\d+)', y[0]).group(1))
#            unseen = int(re.search('UNSEEN\s+(\d+)', y[0]).group(1))
#            return (messages, unseen)
#        except:
#            return False, 0
#
#if __name__ == "__main__":
#    indicator = CheckGMail()
#    indicator.main()

import sys
import gtk
import appindicator
import subprocess
import os

repo_name = "Name Of Indicator"

def sh_escape(s):
    return s.replace("\"","\\\"")

class Commands:
    def __init__(self, title="Unknown", command=""):
        self.title = title
        self.command = command

commandArr = [];
commandArr.append(Commands("Command 1 name","command one"))
commandArr.append(Commands("Command 2 name","command two"))


class RemoteApplet:
    def __init__(self):
        self.ind = appindicator.Indicator(repo_name,
                                           repo_name,
                                           appindicator.CATEGORY_APPLICATION_STATUS)

        self.ind.set_label(repo_name)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("new-messages-red")

        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()
        self.command_items = []
        cnt = 0
        for x in commandArr:
            self.command_items.append(gtk.MenuItem(x.title))
            self.command_items[-1].connect("activate", self.handle_item, cnt)
            self.command_items[-1].show()
            self.menu.append(self.command_items[-1])
            cnt += 1
        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.login()
        print "Started!"
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def login(self):
        pass

    def handle_item(self, widget, index):
        print "Running... " + commandArr[index].command
        proc = subprocess.Popen(commandArr[index].command,stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        os.system("/usr/bin/notify-send \"" + sh_escape(repo_name + " - Output") + "\" \"" + sh_escape(out) + "\"")

if __name__ == "__main__":
    print "Starting..."
    indicator = RemoteApplet()
    indicator.main()