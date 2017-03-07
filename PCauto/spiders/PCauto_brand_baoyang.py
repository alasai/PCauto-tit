# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBaoyangItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoBaoyangSpider(RedisSpider):
    name = 'PCauto_baoyang'
    pipeline = set([pipelines.BaoyangPipeline, ])

    def start_requests(self):
        baoyang_urls = mongoservice.get_brand_baoyang()
        for url in baoyang_urls:
            yield Request(url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBaoyangItem()

        result['category'] = '车系-保养'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

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