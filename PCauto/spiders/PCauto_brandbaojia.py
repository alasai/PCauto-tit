# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.mongodb import mongoservice
from PCauto.items import PCautoBrandbaojiaUrlItem
from PCauto import pipelines

class PCautoBrandBaojiaSpider(RedisSpider):
    name = 'PCauto_baojia'
    pipeline = set([pipelines.BrandBaojiaPipeline, ])

    def start_requests(self):
        baojia_urls = mongoservice.get_baojia_url()
        for url in baojia_urls :
            yield Request(url, dont_filter=True, callback=self.get_vehicleTypes)
            yield Request(url, callback=self.get_url)


    def get_vehicleTypes(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        vehicleList = soup.find('div',id="typeList")
        if vehicleList:
            saleTypes = vehicleList.find_all('div',class_='contentdiv')
            for type in saleTypes:
                vehicles = type.find('ul').find_all('li')
                for vehicle in vehicles:
                    href = vehicle.find('a').get('href')
                    yield Request(href, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandbaojiaUrlItem()

        result['category'] = '报价'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text = place.get_text().strip().replace('\n','')
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