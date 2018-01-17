# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para breakingbaditastreaming.altervista.org
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

__channel__ = "breakingbadita"
__category__ = "S"
__type__ = "generic"
__title__ = "BreakingBadITA Streaming"
__language__ = "IT"

host = "http://breakingbaditastreaming.altervista.org/"

DEBUG = config.get_setting("debug")


def isGeneric():
    return True


def mainlist(item):
    logger.info("[breakingbadita.py] mainlist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(host)

    patronvideos = '<li><a href="([^"]+)"><span class="catTitle">([^<]+)<\/span>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)
    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(2))
        scrapedurl = host + match.group(1)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="listepisodes",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl))

    return itemlist


def listepisodes(item):
    logger.info("[breakingbadita.py] episodeslist")
    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patronvideos = '<h3 class="catItemTitle">\s*<a href="([^"]+)">([^<]+)<\/a>'
    matches = re.compile(patronvideos, re.DOTALL).finditer(data)

    for match in matches:
        scrapedtitle = scrapertools.unescape(match.group(2)).strip()
        scrapedurl = host + match.group(1)
        if DEBUG: logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "]")

        # Añade al listado de XBMC
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle,
                 show=item.show,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="listepisodes",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="listepisodes",
                 show=item.show))

    return itemlist
