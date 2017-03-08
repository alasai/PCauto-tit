# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoDealerContactItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerContactSpider(RedisSpider):
    name = 'PCauto_dealer_contact'
    pipeline = set([pipelines.DealerContactPipeline, ])

    def start_requests(self):
        contact_urls = mongoservice.get_dealer_contact()
        for url in contact_urls:
            yield Request(url, dont_filter=True, callback=self.get_contacts)
            yield Request(url, callback=self.get_url)

    def get_contacts(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        tabs = soup.find('div', class_="ctltag").find_all('a')
        for tab in tabs[1:]:
            href = tab.get('href')
            yield Request(href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerContactItem()
        result['category'] = '经销商-联系我们'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
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