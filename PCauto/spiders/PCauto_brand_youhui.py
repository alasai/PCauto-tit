# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoYouhuiItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoBrandYouhuiSpider(RedisSpider):
    name = 'PCauto_brand_youhui'
    pipeline = set([pipelines.YouhuiPipeline, ])

    def start_requests(self):
        youhui_urls = mongoservice.get_brand_youhui()
        for url in youhui_urls:
            yield Request(url+'r2/', callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoYouhuiItem()

        result['category'] = '车系-优惠'
        result['tit'] = soup.find('title').get_text().strip()

        # cut url
        url_ma = re.match(r'(.+)r2',response.url)
        result['url'] = url_ma.group(1)

        place = soup.find('div',class_="position")
        if place:
            text = place.find('div',class_="pos-mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for half minute to close the spider')
        time.sleep(30)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')