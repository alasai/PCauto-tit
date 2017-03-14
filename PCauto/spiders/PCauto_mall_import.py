# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from PCauto.items import PCautoMallImportItem
import time
from PCauto import pipelines


class PCautoMallImportSpider(RedisSpider):
    name = 'PCauto_mall_import'
    api_url = 'http://mall.pcauto.com.cn%s'
    mall_import = 'http://mall.pcauto.com.cn/import/nb/'

    pipeline = set([pipelines.MallImportPipeline, ])

    def start_requests(self):
        yield Request(self.mall_import, callback=self.get_brand)

    def get_brand(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        brands = soup.find('div', class_='right').find_all('a')
        for brand in brands :
            href = brand.get('href')
            yield Request(self.api_url % href, callback=self.get_car)

    def get_car(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        cars = soup.find('div', id='Jlist').find_all('li')
        for car in cars:
            href = car.find('a').get('href')
            yield Request(self.api_url % href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoMallImportItem()

        result['category'] = '汽车商城-平行进口车'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for ten seconds to close the spider')
        time.sleep(10)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')

