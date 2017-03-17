# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings
from scrapy import log
import functools


# class PcautoPipeline(object):
#     def process_item(self, item, spider):
#         return item

def check_spider_pipeline(process_item_method):

    """
    此方法用于检验不同的spider所对应处理item的pipeline
    :param process_item_method:
    :return:
    """
    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            # print(spider.pipeline)
            spider.log(msg % 'executing', level=log.DEBUG)
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            # spider.log(msg % 'skipping', level=log.DEBUG)
            return item

    return wrapper

# take out the mongodb connecting method
def get_mongo_collection(key):
    connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
    db = connection[settings['MONGODB_DB']]
    return db.get_collection(key)


class BrandInfoPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('BrandInfo')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class PicUrlPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Picture')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class BrandConfigPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Config')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class BrandBaojiaPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('BrandBaojia')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class YouhuiPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Youhui')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class ChedaiPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Chedai')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item


class UsedCarPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('UsedCar')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class ArticlePipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Article')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class CommentPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Comment')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class OwnerPricePipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('OwnerPrice')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class BaoyangPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('BrandBaoyang')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class ForumPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('Forum')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item


class DealerContactPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('DealerContact')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class DealerModelPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('DealerModel')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class DealerMarketPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('DealerMarket')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class DealerNewsPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('DealerNews')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class MallGCTPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('MallGCT')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item

class MallImportPipeline(object):
    def __init__(self):
        self.collection = get_mongo_collection('MallImport')

    @check_spider_pipeline
    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
