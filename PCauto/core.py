# -*- coding: utf-8 -*-

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.log import configure_logging

from spiders.PCauto_start_urls import PCautoBrandListUrlSpider
from spiders.PCauto_brandinfo import PCautoBrandinfoSpider
from spiders.PCauto_brandconfig import PCautoBrandConfigSpider
from spiders.PCauto_brandbaojia import PCautoBrandBaojiaSpider
from spiders.PCauto_usedcar import PCautoUsedcarSpider
from spiders.PCauto_brandArticle import PCautoArticleSpider
from spiders.PCauto_picture import PCautoBrandPictureSpider
from spiders.PCauto_youhui import PCautoBrandYouhuiSpider

import pymongo

# the spider we need to scheduler
BaojiaUrlSpider = PCautoBrandBaojiaSpider()
ConfigSpider = PCautoBrandConfigSpider()
BrandInfoSpider = PCautoBrandinfoSpider()
PCautoStartSpider = PCautoBrandListUrlSpider()
UsedCarUrlSpider = PCautoUsedcarSpider()
ArticleSpider = PCautoArticleSpider()
PictureSpider = PCautoBrandPictureSpider()
BrandYouhuiSpider = PCautoBrandYouhuiSpider()

connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
db = connection[settings['MONGODB_DB']]

configure_logging(settings)
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl():
    # yield runner.crawl(PCautoStartSpider)
    # yield runner.crawl(BrandInfoSpider)
    # yield runner.crawl(ConfigSpider)
    # yield runner.crawl(BaojiaUrlSpider)
    # yield runner.crawl(UsedCarUrlSpider)
    # yield runner.crawl(ArticleSpider)
    # yield runner.crawl(PictureSpider)
    yield runner.crawl(BrandYouhuiSpider)
    reactor.stop()


crawl()
reactor.run()  # the script will block here until the last crawl call is finished