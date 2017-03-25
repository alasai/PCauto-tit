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

class PCautoYouhuiItem(BaseItem):
    pass

class PCautoCommentItem(BaseItem):
    pass

class PCautoOwnerPriceItem(BaseItem):
    pass

class PCautoBaoyangItem(BaseItem):
    pass

class PCautoForumItem(BaseItem):
    pass

class PCautoDealerItem(BaseItem):
    pass

class PCautoVideoItem(BaseItem):
    pass

class PCautoHangqingItem(BaseItem):
    pass

class PCautoNewCarItem(BaseItem):
    pass

class PCautoDaogouItem(BaseItem):
    pass

class PCautoPingceItem(BaseItem):
    pass

class PCautoTechItem(BaseItem):
    pass

class PCautoYanghuItem(BaseItem):
    pass

class PCautoTireItem(BaseItem):
    pass

class PCautoMachineOilItem(BaseItem):
    pass

class PCautoGaizhuangItem(BaseItem):
    pass

class PCautoHangyeItem(BaseItem):
    pass

class PCautoMotoSportItem(BaseItem):
    pass

class PCautoCultureItem(BaseItem):
    pass




class PCautoDealerContactItem(SimpleItem):
    pass

class PCautoDealerModelItem(SimpleItem):
    pass

class PCautoDealerMarketItem(SimpleItem):
    pass

class PCautoDealerNewsItem(SimpleItem):
    pass

class PCautoMallGCTItem(SimpleItem):
    pass

class PCautoMallImportItem(SimpleItem):
    pass

class PCautoChedaiItem(SimpleItem):
    pass
