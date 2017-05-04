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

def save_vehicleType(result):
    collection = db['VehicleType']
    collection.save(result)

def save_dealer(result):
    collection = db['Dealer']
    collection.save(result)

def save_dealer_index(result):
    collection = db['DealerIndex']
    collection.save(result)

def save_dealer_other(result):
    collection = db['DealerOther']
    collection.save(result)


def get_config_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'config_url' in brand.keys():
            starturls.add(brand['config_url'])
    return starturls

def get_baojia_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'baojia_url' in brand.keys():
            starturls.add(brand['baojia_url'])
    return starturls

def get_usedcar_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'used_car_url' in brand.keys():
            starturls.add(brand['used_car_url'])
    return starturls

def get_article_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'article_url' in brand.keys():
            starturls.add(brand['article_url'])
    return starturls

def get_pic_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'pic_url' in brand.keys():
            starturls.add(brand['pic_url'])
    return starturls

def get_brand_youhui():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'youhui_url' in brand.keys():
            starturls.add(brand['youhui_url'])
    return starturls

def get_comment_url():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'comment_url' in brand.keys():
            starturls.add(brand['comment_url'])
    return starturls

def get_owner_price():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'owner_price_url' in brand.keys():
            starturls.add(brand['owner_price_url'])
    return starturls

def get_brand_baoyang():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'baoyang_url' in brand.keys():
            starturls.add(brand['baoyang_url'])
    return starturls

def get_brand_forum():
    collection = db['Brand']
    starturls = set()
    for brand in collection.find({}):
        if 'forum_url' in brand.keys():
            starturls.add(brand['forum_url'])
    return starturls

def get_fenqi_url():
    collection = db['Brand']
    starturls = set()
    for doc in collection.find({'fenqi_url':{'$exists':True}},{'fenqi_url':1,'_id':0}):
        starturls.add(doc['fenqi_url'])
    return starturls


def get_dealer_contact():
    collection = db['Dealer']
    starturls = set()
    for dealer in collection.find({}):
        if 'contact_url' in dealer.keys():
            starturls.add(dealer['contact_url'])
    return starturls

def get_dealer_model():
    collection = db['Dealer']
    starturls = set()
    for dealer in collection.find({}):
        if 'model_url' in dealer.keys():
            starturls.add(dealer['model_url'])
    return starturls

def get_dealer_market():
    collection = db['Dealer']
    starturls = set()
    for dealer in collection.find({}):
        if 'market_url' in dealer.keys():
            starturls.add(dealer['market_url'])
    return starturls

def get_vehicleType():
    collection = db['VehicleType']
    starturls = set()
    for doc in collection.find({'url':{'$exists':True}},{'url':1,'_id':0}):
        starturls.add(doc['url'])
    return starturls

