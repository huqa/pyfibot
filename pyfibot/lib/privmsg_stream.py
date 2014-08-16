# -*- coding: utf-8 -*-
"""
Created on 16.01.2014

@author: huqa // Ville Riikonen <pikkuhukka@gmail.com>
@copyright Copyright (c) 2014 Ville Riikonen
@license BSD
"""


class PrivmsgStream(object):
    """
    A simple stream wrapper that implements write() and flush()
    Outputs any gotten input to bot admins that have flagged !irclogger to true
    @TODO: research possibility of dcc chat instead of privmsg
    """
    def __init__(self, bot=None):
        self.bot = bot

    def write(self, string):
        """Gets input as string and outputs it to admins"""
        if self.bot:
            admins = self.bot.get_admins()
            for admin in admins:
                if admin in self.bot.log_streamers:
                    if self.bot.log_streamers[admin]:
                        self.bot.say(admin, string)

    def flush(self):
        """Not needed?"""
        pass
