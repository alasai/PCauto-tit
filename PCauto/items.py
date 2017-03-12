# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field

class BaseItem(Item):
    tit = Field()
    url = Field()
    address = Field()
    category = Field()

class SimpleItem(Item):
    tit = Field()
    url = Field()
    category = Field()


class PCautoBrandinfoItem(BaseItem):
    pass

class PCautoBrandPictureUrlItem(BaseItem):
    pass

class PCautoBrandConfigItem(BaseItem):
    pass

class PCautoBrandbaojiaUrlItem(BaseItem):
    pass

class PCautoUsedCarItem(BaseItem):
    pass

class PCautoBrandArticleItem(BaseItem):
    pass

class PCautoBrandYouhuiItem(BaseItem):
    pass

class PCautoCommentItem(BaseItem):
    pass

class PCautoOwnerPriceItem(BaseItem):
    pass

class PCautoBaoyangItem(BaseItem):
    pass

class PCautoForumItem(BaseItem):
    pass

class PCautoDealerContactItem(SimpleItem):
    pass

class PCautoDealerModelItem(SimpleItem):
    pass

class PCautoDealerMarketItem(SimpleItem):
    pass

class PCautoDealerNewsItem(SimpleItem):
    pass


