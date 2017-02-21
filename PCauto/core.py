# -*- coding: utf-8 -*-
import scrapy
import scrapy_redis

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.log import configure_logging

from spiders.PCauto_start_urls import PCautoBrandListUrlSpider

import os
import pymongo
import json

# the spider we need to scheduler
# ArticleSpider = AutohomeArticleSpider()
# BaikeSpider = AutohomeBaikeSpider()
# BaojiaUrlSpider = AutohomeBaojiaSpider()
# ConfigSpider = AutohomeConfigSpider()
# BrandInfoSpider = AutohomeBrandInfoSpider()
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
# UsedCarUrlSpider = AutohomeUsedCarUrlSpider()
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
    # yield runner.crawl(UrlSpider)
    # yield runner.crawl(BrandListUrlSpider)
    # yield runner.crawl(DealerlistSpider)
    # yield runner.crawl(BrandInfoSpider)
    # yield runner.crawl(BaikeSpider)
    # yield runner.crawl(ArticleSpider)
    # yield runner.crawl(DetailedVehicleUrlSpider)
    # yield runner.crawl(ConfigSpider)
    # # yield runner.crawl(ForumSpider)
    yield runner.crawl(PCautoStartSpider)
    reactor.stop()


crawl()
reactor.run()  # the script will block here until the last crawl call is finished