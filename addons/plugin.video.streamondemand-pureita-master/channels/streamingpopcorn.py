# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para streamingpopcorn
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "streamingpopcorn"
__category__ = "F"
__type__ = "generic"
__title__ = "streamingpopcorn (IT)"
__language__ = "IT"

DEBUG = config.get_setting("debug")

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding', 'gzip, deflate']
]

host = "http://streamingpopcorn.com/portal/"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.streamingpopcorn mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi Film Inseriti[/COLOR]",
                     action="peliculas",
                     url=host + "?internet",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_cinema_P.png")]

    return itemlist


def peliculas(item):
    logger.info("streamondemand.streamingpopcorn peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url, headers=headers)

    # Extrae las entradas (carpetas)
    patron = '<img style="[^"]+" rel="image_src" src="(.*?)" />.*?'
    patron += '<h4 class="widgettitle"><a href="([^"]+)">\s*(.*?)</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(host, scrapedurl)
        scrapedthumbnail = urlparse.urljoin(host, scrapedthumbnail)
        html = scrapertools.cache_page(scrapedurl, headers=headers)
        start = html.find("</figure>")
        end = html.find("</div>", start)
        scrapedplot = html[start:end]
        scrapedplot = re.sub(r'<[^>]*>', '', scrapedplot)
        scrapedplot = scrapertools.decodeHtmlentities(scrapedplot)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle.strip()
        #scrapedthumbnail = ""
        if (DEBUG): logger.info(
                "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(
                Item(channel=__channel__,
                     action="play",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                     url=scrapedurl,
                     thumbnail=scrapedthumbnail,
                     plot=scrapedplot,
                     folder=True))

    # Extrae el paginador
    patron = '<a href="([^"]+)">Pagina successiva</a>'
    match = scrapertools.find_single_match(data, patron)

    if match != '':
        scrapedurl = urlparse.urljoin(host, match)
        itemlist.append(
                Item(channel=__channel__,
                     action="peliculas",
                     title="[COLOR orange]Successivo>>[/COLOR]",
                     url=scrapedurl,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                     folder=True))

    return itemlist


def play(item):
    logger.info("[streamingpopcorn.py] play")

    data = scrapertools.cache_page(item.url, headers=headers)

    path = scrapertools.find_single_match(data, "href='(linker.php.id=[^']+)'")
    url = urlparse.urljoin(host, path)
    location = scrapertools.get_header_from_response(url, header_to_get="Location")

    itemlist = servertools.find_video_items(data=location)

    for videoitem in itemlist:
        videoitem.title = item.show
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
