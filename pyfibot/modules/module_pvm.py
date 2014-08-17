# -*- coding: utf-8 -*-
"""
Created on 10.9.2012

@author: huqa // Ville Riikonen <pikkuhukka@gmail.com>
@copyright Copyright (c) 2012,2014 Ville Riikonen
@license BSD
"""

from ..lib import pvm
from math import ceil, sqrt
from operator import itemgetter
import logging
log = logging.getLogger("pvm")


def command_pvm(bot, user, channel, args):
    pvm_obj = bot.get_pvm()
    pvm_obj.shout_pvm_stats_to_chan(channel)


def command_toptod(bot, user, channel, args):
    words_str = ""
    toptod = bot.get_words()
    if channel in toptod:
        stats = toptod[channel]
        #only top 10 now
        sorted_stats = sorted(stats.iteritems(), key=itemgetter(1))[0:10]
        sorted_stats.reverse()
        sija = 1
        all = 0
        med_sija = int(ceil(len(sorted_stats) / 2.0))
        median = 0
        for x in sorted_stats:
            if sija is med_sija:
                median = x[1]
            words_str += "%d. %s:(%d) " % (sija, str(x[0]), x[1])
            sija += 1
            all += x[1]
        mean = all / (sija - 1)
        var_summa = 0
        for x in sorted_stats:
            var_summa += ((x[1] - mean)**2)
        keskihajonta = sqrt((var_summa/float((sija - 1))))
        bot.say(channel, words_str)
        bot.say(channel, "Top 10 yhteensä: %d Keskiarvo: %d Mediaani: %d Keskihajonta: %d" % (all, mean, median, keskihajonta))
        return top_all(bot, channel, stats)
    else:
        return

def top_all(bot, channel, stats):
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
        return bot.say(channel, "Kaikki yhteensä: %d Keskiarvo: %d Mediaani: %d Keskihajonta: %d" % (all, mean, median, keskihajonta))    
