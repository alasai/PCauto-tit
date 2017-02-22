# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import re
import time
import json
from PCauto.items import PCautoBrandConfigItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoBrandConfigSpider(RedisSpider):
    name = 'PCauto_config'
    pipeline = set([pipelines.BrandConfigPipeline, ])

    def start_requests(self):
        config_urls = mongoservice.get_config_url()
        for url in config_urls:
            yield Request(url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandConfigItem()

        result['category'] = '车系-参数配置'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
        place=soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text=place.get_text().strip().replace('\n','')
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