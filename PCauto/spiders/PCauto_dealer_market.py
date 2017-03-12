# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoDealerMarketItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerMarketSpider(RedisSpider):
    name = 'PCauto_dealer_market'
    pipeline = set([pipelines.DealerMarketPipeline, ])
    root_url = 'http://price.pcauto.com.cn'

    def start_requests(self):
        urls = mongoservice.get_dealer_market()
        for url in urls:
            yield Request(url, dont_filter=True, callback=self.get_market_info)
            yield Request(url, callback=self.get_url)

    def get_market_info(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        market_info_list = soup.find('ul', class_='cxyhlt clearfix').find_all('li')
        for market_info in market_info_list:
            href = market_info.find('div', class_='wbtag').find('a').get('href')
            yield Request(href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerMarketItem()
        result['category'] = '经销商-促销优惠'
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