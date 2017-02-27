# -*- coding: utf-8 -*-
import scrapy
import scrapy_redis

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.log import configure_logging

from spiders.PCauto_start_urls import PCautoBrandListUrlSpider
from spiders.PCauto_brandinfo import PCautoBrandinfoSpider
from spiders.PCauto_brandconfig import PCautoBrandConfigSpider
from spiders.PCauto_brandbaojia import PCautoBrandBaojiaSpider
from spiders.PCauto_usedcar import PCautoUsedcarSpider

# import os
import pymongo
# import json

# the spider we need to scheduler
# ArticleSpider = AutohomeArticleSpider()
# BaikeSpider = AutohomeBaikeSpider()
BaojiaUrlSpider = PCautoBrandBaojiaSpider()
ConfigSpider = PCautoBrandConfigSpider()
BrandInfoSpider = PCautoBrandinfoSpider()
# BrandListUrlSpider = AutohomeBrandListUrlSpider()
# CarStoreSpider = AutohomeCarStoreSpider()
# DealerSpider = AutohomeDealerSpider()
# DealerinfoSpider = AutohomeDealerinfoSpider
# InformatioSpider = AutohomeDealerinformatioSpider()
# DealerlistSpider = AutohomeDealerlistSpider()
# DealernewsSpider = AutohomeDealernewsSpider()
# DealerpriceSpider = AutohomeDealerpriceSpider()
# DealersalerlistSpider = AutohomeDealersalerlistSpider()
# DetailedVehicleUrlSpider = AutohomeDetailedVehicleUrlSpider()
# ForumSpider = AutohomeForumSpider()
# UrlSpider = AutohomeUrlSpider()
PCautoStartSpider = PCautoBrandListUrlSpider()
# DealermaintainSpider = AutohomeDealermaintainSpider()
# OwnerpriceSpider = AutohomeOwnerpriceSpider()
# PicUrlSpider = AutohomePicUrlSpider()
# ShuoKeSpider = AutohomeShuoKeSpider()
UsedCarUrlSpider = PCautoUsedcarSpider()
# VideoUrlSpider = AutohomeVideoUrlSpider()
# YouChuangSpider = AutohomeYouChuangSpider()
# ZhiDaoUrlSpider = AutohomeZhiDaoUrlSpider()
# ForumsSpider = AutohomeForumsSpider()

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
    yield runner.crawl(UsedCarUrlSpider)
    reactor.stop()


crawl()
reactor.run()  # the script will block here until the last crawl call is finished