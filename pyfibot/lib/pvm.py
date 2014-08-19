# -*- coding: utf-8 -*-
"""
Created on 9.9.2012

@author: huqa // Ville Riikonen <pikkuhukka@gmail.com>
@copyright Copyright (c) 2012,2014 Ville Riikonen
@license BSD
"""

import datetime
import time
from math import ceil, sqrt
import namedays as nday
from operator import itemgetter


class Pvm(object):

    def __init__(self, bot):
        self.bot = bot
        self.channels = []
        
    # remind every day at midnight
    def midnight_shout(self):
        #self.bot.scheduler.add_cron_job(self.shout_pvm_stats, second='0', month='*', day='*', hour='0', minute='0', day_of_week='*')
        self.bot.scheduler.add_job(self.shout_pvm_stats, 'cron', month='*', day='*', day_of_week='*', hour='0', minute='0', second='0')

    def shout_pvm_stats(self):
        """Internal command for shouting word stats and day info at midnight"""
        if not self.bot:
            return

        if not self.channels:
            self.channels = self.bot.get_channels_for_stats()
        ds = time.localtime()
        weekn = datetime.date(ds.tm_year, ds.tm_mon, ds.tm_mday).isocalendar()[1]
        outstr = "Tänään on " + nday.wday_str(ds.tm_wday) + " " + str(ds.tm_mday) + "." \
                    + str(ds.tm_mon) + "." + str(ds.tm_year) + " (viikko " + str(weekn) +") vuoden " + str(ds.tm_yday) + ". päivä. Nimipäivää viettää " + nday.get_nameday(ds.tm_mon,ds.tm_mday)
        toptod = self.bot.get_words()
        words_str = ""
        for ch in self.channels:
            time.sleep(10)
            if ch in toptod:    
                stats = toptod[ch]
                sorted_stats = sorted(stats.iteritems(), key=itemgetter(1))[0:10]
                sorted_stats.reverse()
                sija = 1
                all = 0
                mean = 0
                words_str = ""
                med_sija = int(ceil(len(sorted_stats) / 2.0))
                median = 0
                for x in sorted_stats:
                    if sija is med_sija:
                        median = x[1]
                    words_str += " %d. %s:(%d)" % (sija, str(x[0]), x[1])
                    sija += 1
                    all += x[1]
                mean = all / (sija - 1)
                var_summa = 0
                for x in sorted_stats:
                    var_summa += ((x[1] - mean)**2)
                keskihajonta = sqrt((var_summa/float((sija - 1))))
                self.bot.say(ch, words_str.strip())
                self.bot.say(ch, "Top 10 yhteensä: %d Keskiarvo: %d Mediaani: %d Keskihajonta: %d" % (all, mean, median, keskihajonta))
                self.top_all(ch, stats)
            self.bot.say(ch, outstr)
        
        self.bot.clear_words()

    def top_all(self, channel, stats):
        sorted_stats = sorted(stats.iteritems(), key=itemgetter(1))
        sorted_stats.reverse()
        sija = 1
        all = 0
        med_sija = int(ceil(len(sorted_stats) / 2.0))
        median = 0
        for x in sorted_stats:
            if sija is med_sija:
                median = x[1]
            sija += 1
            all += x[1]
        mean = all / (sija - 1)
        var_summa = 0
        for x in sorted_stats:
            var_summa += ((x[1] - mean)**2)
        keskihajonta = sqrt((var_summa/float((sija - 1))))
        self.bot.say(channel, "Kaikki yhteensä: %d Keskiarvo: %d Mediaani: %d Keskihajonta: %d" % (all, mean, median, keskihajonta))   

    def shout_pvm_stats_to_chan(self, chan):
        if not self.bot:
            return
        
        if not chan:
            return
        
        ds = time.localtime()
        weekn = datetime.date(ds.tm_year, ds.tm_mon, ds.tm_mday).isocalendar()[1]
        outstr = "Tänään on " + nday.wday_str(ds.tm_wday) + " " + str(ds.tm_mday) + "." \
                    + str(ds.tm_mon) + "." + str(ds.tm_year) + " (viikko " + str(weekn) +") vuoden " + str(ds.tm_yday) + ". päivä. Nimipäivää viettää " + nday.get_nameday(ds.tm_mon,ds.tm_mday)

        self.bot.say(chan, outstr)
