# -*- coding: utf-8 -*-
"""Displays HTML page titles

Smart title functionality for sites which could have clear titles,
but still decide show idiotic bulk data in the HTML title element

$Id$
$HeadURL$
"""

import fnmatch
import urlparse
import logging
import re
try:
    import json
    has_json = True
except:
    print "Unable to load json, not all title features will work"

from types import TupleType

from util.BeautifulSoup import BeautifulStoneSoup

log = logging.getLogger("urltitle")
config = None


def init(bot):
    global config
    config = bot.config.get("module_urltitle", {})


def handle_url(bot, user, channel, url, msg):
    """Handle urls"""

    if msg.startswith("-"):
        return
    if re.match("http://.*?\.imdb\.com/title/tt([0-9]+)/?", url):
        return  # IMDB urls are handled elsewhere
    if re.match("(http:\/\/open.spotify.com\/|spotify:)(album|artist|track)([:\/])([a-zA-Z0-9]+)\/?", url):
        return  # spotify handled elsewhere

    if channel.lstrip("#") in config.get('disable', ''):
        return

    # hack, support both ignore and ignore_urls for a while
    for ignore in config.get("ignore", []):
        if fnmatch.fnmatch(url, ignore):
            log.info("Ignored URL: %s %s", url, ignore)
            return
    for ignore in config.get("ignore_urls", []):
        if fnmatch.fnmatch(url, ignore):
            log.info("Ignored URL: %s %s", url, ignore)
            return
    for ignore in config.get("ignore_users", []):
        if fnmatch.fnmatch(user, ignore):
            log.info("Ignored url from user: %s, %s %s", user, url, ignore)
            return

    # a crude way to handle the new-fangled shebang urls as per
    # http://code.google.com/web/ajaxcrawling/docs/getting-started.html
    # this can manage twitter + gawker sites for now
    url = url.replace("#!", "?_escaped_fragment_=")

    handlers = [(h, ref) for h, ref in globals().items() if h.startswith("_handle_")]

    # try to find a specific handler for the URL
    for handler, ref in handlers:
        pattern = ref.__doc__.split()[0]
        if fnmatch.fnmatch(url, pattern):
            title = ref(url)
            if title:
                # handler found, abort
                return _title(bot, channel, title, True)

    bs = getUrl(url).getBS()
    if not bs:
        log.debug("No BS available, returning")
        return

    title = bs.first('title')
    # no title attribute
    if not title:
        log.debug("No title found, returning")
        return

    try:
        # remove trailing spaces, newlines, linefeeds and tabs
        title = title.string.strip()
        title = title.replace("\n", " ")
        title = title.replace("\r", " ")
        title = title.replace("\t", " ")

        # compress multiple spaces into one
        title = re.sub("[ ]{2,}", " ", title)

        # nothing left in title (only spaces, newlines and linefeeds)
        if not title:
            return

        if _check_redundant(url, title):
            log.debug("Redundant title, not displaying")
            return

        return _title(bot, channel, title)

    except AttributeError:
        # TODO: Nees a better way to handle this. Happens with empty <title> tags
        pass


def _check_redundant(url, title):
    """Returns true if the url and title are similar enough."""
    # Remove hostname from the title
    hostname = urlparse.urlparse(url.lower()).netloc
    hostname = ".".join(hostname.split('@')[-1].split(':')[0].lstrip('www.').split('.'))
    cmp_title = title.lower()
    for part in hostname.split('.'):
        idx = cmp_title.replace(' ', '').find(part)
        if idx != -1:
            break

    if idx > len(cmp_title) / 2:
        cmp_title = cmp_title[0:idx + (len(title[0:idx]) - len(title[0:idx].replace(' ', '')))].strip()
    elif idx == 0:
        cmp_title = cmp_title[idx + len(hostname):].strip()
    # Truncate some nordic letters
    unicode_to_ascii = {u'\u00E4': 'a', u'\u00C4': 'A', u'\u00F6': 'o', u'\u00D6': 'O', u'\u00C5': 'A', u'\u00E5': 'a'}
    for i in unicode_to_ascii:
        cmp_title = cmp_title.replace(i, unicode_to_ascii[i])

    cmp_url = url.replace("-", " ")
    cmp_url = url.replace("+", " ")
    cmp_url = url.replace("_", " ")

    parts = cmp_url.lower().rsplit("/")

    distances = []
    for part in parts:
        if part.rfind('.') != -1:
            part = part[:part.rfind('.')]
        distances.append(_levenshtein_distance(part, cmp_title))

    if len(title) < 20 and min(distances) < 5:
        return True
    elif len(title) >= 20 and len(title) <= 30 and min(distances) < 10:
        return True
    elif len(title) > 30 and len(title) <= 60 and min(distances) <= 21:
        return True
    elif len(title) > 60 and min(distances) < 37:
        return True
    return False


def _levenshtein_distance(s, t):
    d = [[i] + [0] * len(t) for i in xrange(0, len(s) + 1)]
    d[0] = [i for i in xrange(0, (len(t) + 1))]

    for i in xrange(1, len(d)):
        for j in xrange(1, len(d[i])):
            if len(s) > i - 1 and len(t) > j - 1 and s[i - 1] == t[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min((d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 1))

    return d[len(s)][len(t)]


def _title(bot, channel, title, smart=False, prefix=None):
    """Say title to channel"""

    if not title: return

    if not prefix:
        prefix = "Title:"
    info = None
    # tuple, additional info
    if type(title) == TupleType:
        info = title[1]
        title = title[0]
    # crop obscenely long titles
    if len(title) > 200:
        title = title[:200] + "..."

    title = BeautifulStoneSoup(title, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    log.info(title)

    if not info:
        return bot.say(channel, "%s '%s'" % (prefix, title))
    else:
        return bot.say(channel, "%s '%s' [%s]" % (prefix, title, info))


# TODO: Some handlers does not have if not bs: return, but why do we even have this for every function
def _handle_iltalehti(url):
    """*iltalehti.fi*html"""
    # Go as normal
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.first('title').string
    # The first part is the actual story title, lose the rest
    title = title.split("|")[0].strip()
    return title


def _handle_iltasanomat(url):
    """*iltasanomat.fi*uutinen.asp*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.title.string.rsplit(" - ", 1)[0]
    return title


def _handle_keskisuomalainen_sahke(url):
    """*keskisuomalainen.net*sahkeuutiset/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.first('p', {'class': 'jotsikko'})
    if title:
        title = title.next.strip()
        return title


def _handle_tietokone(url):
    """http://www.tietokone.fi/uutta/uutinen.asp?news_id=*"""
    bs = getUrl(url).getBS()
    sub = bs.first('h5').string
    main = bs.first('h2').string
    return "%s - %s" % (main, sub)


def _handle_itviikko(url):
    """http://www.itviikko.fi/*/*/*/*/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    return bs.first("h1", "headline").string

def _handle_verkkokauppa(url):
    """http://www.verkkokauppa.com/*/product/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    product = bs.first('h1', id='productName').string
    price = bs.first('span', {'class': 'hintabig'}).string
    return "%s | %s" % (product, price)


def _handle_mol(url):
    """http://www.mol.fi/paikat/Job.do?*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.first("div", {'class': 'otsikko'}).string
    return title

def _handle_tweet2(url):
    """http*://twitter.com/*/status/*"""
    return _handle_tweet(url)

def _handle_tweet(url):
    """http*://twitter.com/*/statuses/*"""
    import simplejson as json
    import urllib2
    tweet_url = "http://api.twitter.com/1/statuses/show/%s.json"
    test = re.match("https?://twitter\.com\/(\w+)/status(es)?/(\d+)",url)
    #    matches for unique tweet id string
    infourl = tweet_url % test.group(3)

    twitapi = urllib2.urlopen(infourl)
    #loads into dict
    json1 = json.load(twitapi)

    #reads dict
    ##You can modify the fields below or add any fields you want to the returned string
    text = json1['text']
    user = json1['user']['screen_name']
    name = json1['user']['name']
    tweet = "Tweet by %s(@%s): %s" % (name, user, text)
    return tweet


def _handle_netanttila(url):
    """http://www.netanttila.com/webapp/wcs/stores/servlet/ProductDisplay*"""
    bs = getUrl(url).getBS()
    itemname = bs.first("h1").string.replace("\n", "").replace("\r", "").replace("\t", "").strip()
    price = bs.first("td", {'class': 'right highlight'}).string.split(" ")[0]
    return "%s | %s EUR" % (itemname, price)


def _handle_youtube_shorturl(url):
    """http*://youtu.be/*"""
    return _handle_youtube_gdata(url)


def _handle_youtube_gdata_new(url):
    """http*://youtube.com/watch#!v=*"""
    return _handle_youtube_gdata(url)


def _handle_youtube_gdata(url):
    """http*://*youtube.com/watch?*v=*"""
    gdata_url = "http://gdata.youtube.com/feeds/api/videos/%s"

    match = re.match("https?://youtu.be/(.*)", url)
    if not match:
        match = re.match("https?://.*?youtube.com/watch\?.*?v=([^&]+)", url)
    if match:
        infourl = gdata_url % match.group(1)
        bs = getUrl(infourl, True).getBS()

        entry = bs.first("entry")

        if not entry:
            log.info("Video too recent, no info through API yet.")
            return

        author = entry.author.next.string
        # if an entry doesn't have a rating, the whole element is missing
        try:
            rating = float(entry.first("gd:rating")['average'])
        except TypeError:
            rating = 0.0

        stars = int(round(rating)) * "*"
        statistics = entry.first("yt:statistics")
        if statistics:
            views = statistics['viewcount']
        else:
            views = "no"
        racy = entry.first("yt:racy")
        media = entry.first("media:group")
        title = media.first("media:title").string
        secs = int(media.first("yt:duration")['seconds'])
        lengthstr = []
        hours, minutes, seconds = secs // 3600, secs // 60 % 60, secs % 60
        if hours > 0:
            lengthstr.append("%dh" % hours)
        if minutes > 0:
            lengthstr.append("%dm" % minutes)
        if seconds > 0:
            lengthstr.append("%ds" % seconds)
        if racy:
            adult = " - XXX"
        else:
            adult = ""
        return "%s by %s [%s - %s - %s views%s]" % (title, author, "".join(lengthstr), "[%-5s]" % stars, views, adult)


def _handle_helmet(url):
    """http://www.helmet.fi/record=*fin"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.find(attr={'class': 'bibInfoLabel'}, text='Teoksen nimi').next.next.next.next.string
    return title


def _handle_ircquotes(url):
    """http://*ircquotes.fi/[?]*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    chan = bs.first("span", {'class': 'quotetitle'}).next.next.string
    points = bs.first("span", {'class': 'points'}).next.string
    firstline = bs.first("div", {'class': 'quote'}).next.string
    title = "%s (%s): %s" % (chan, points, firstline)
    return title


def _handle_alko2(url):
    """http://alko.fi/tuotteet/fi/*"""
    return _handle_alko(url)


def _handle_alko(url):
    """http://www.alko.fi/tuotteet/fi/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    name = bs.find('span', {'class': 'tuote_otsikko'}).string
    price = bs.find('span', {'class': 'tuote_hinta'}).string.split(" ")[0] + u"€"
    drinktype = bs.find('span', {'class': 'tuote_tyyppi'}).next
    return name + " - " + drinktype + " - " + price


def _handle_salakuunneltua(url):
    """*salakuunneltua.fi*"""
    return None


def _handle_facebook(url):
    """*facebook.com/*"""
    if not has_json: return
    if re.match("http(s?)://(.*?)facebook\.com/(.*?)id=(\\d+)", url):
        asd = urlparse.urlparse(url)
        id = asd.query.split('id=')[1].split('&')[0]
        if id != '':
            url = "https://graph.facebook.com/%s" % id
            content = getUrl(url, True).getContent()
            if content != 'false':
                data = json.loads(content)
                try:
                    title = data['name']
                except:
                    return
            else:
                title = 'Private url'
    else:
        return
    return title


def _handle_vimeo(url):
    """*vimeo.com/*"""
    data_url = "http://vimeo.com/api/v2/video/%s.xml"
    match = re.match("http://.*?vimeo.com/(\d+)", url)
    if match:
        infourl = data_url % match.group(1)
        bs = getUrl(infourl, True).getBS()
        title = bs.first("title").string
        user = bs.first("user_name").string
        likes = bs.first("stats_number_of_likes").string
        plays = bs.first("stats_number_of_plays").string
        return "%s by %s [%s likes, %s views]" % (title, user, likes, plays)


def _handle_stackoverflow(url):
    """*stackoverflow.com/questions/*"""
    if not has_json: return
    api_url = 'http://api.stackoverflow.com/1.1/questions/%s'
    match = re.match('.*stackoverflow.com/questions/([0-9]+)', url)
    if match is None:
        return
    question_id = match.group(1)
    content = getUrl(api_url % question_id, True).getContent()
    if not content:
        log.debug("No content received")
        return
    try:
        data = json.loads(content)
        title = data['questions'][0]['title']
        tags = "/".join(data['questions'][0]['tags'])
        score = data['questions'][0]['score']
        return "%s - %dpts - %s" % (title, score, tags)
    except Exception, e:
        return "Json parsing failed %s" % e


def _handle_hs(url):
    """*hs.fi*artikkeli*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.title.string
    title = title.split("-")[0].strip()
    try:
        # determine article age and warn if it is too old
        from datetime import datetime
        # handle updated news items of format, and get the latest update stamp
        # 20.7.2010 8:02 | PÃ¤ivitetty: 20.7.2010 12:53
        date = bs.first('p', {'class': 'date'}).next
        # in case hs.fi changes the date format, don't crash on it
        if date:
            date = date.split("|")[0].strip()
            article_date = datetime.strptime(date, "%d.%m.%Y %H:%M")
            delta = datetime.now() - article_date

            if delta.days > 365:
                return title, "NOTE: Article is %d days old!" % delta.days
            else:
                return title
        else:
            return title
    except Exception, e:
        log.error("Error when parsing hs.fi: %s" % e)
        return title

def _handle_mtv3(url):
    """*mtv3.fi*"""
    bs = getUrl(url).getBS()
    title = bs.first("h1", "otsikko").next
    return title


def _handle_yle(url):
    """http://*yle.fi/uutiset/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.title.string
    title = title.split("|")[0].strip()
    return title


def _handle_varttifi(url):
    """http://www.vartti.fi/artikkeli/*"""
    bs = getUrl(url).getBS()
    title = bs.first("h2").string
    return title


def _handle_aamulehti(url):
    """http://www.aamulehti.fi/*"""
    bs = getUrl(url).getBS()
    if not bs:
        return
    title = bs.fetch("h1")[0].string
    return title


def _handle_apina(url):
    """http://apina.biz/*"""
    return None