import pymongo
from scrapy.conf import settings

connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
db = connection[settings['MONGODB_DB']]



def save_brandlist(result):
    collection = db['Brand']
    collection.save(result)

def save_brandInfo(result):
    collection = db['BrandInfo']
    collection.save(result)

def get_config_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'config_url' in brand.keys():
            starturls.add(brand['config_url'])
    return starturls
