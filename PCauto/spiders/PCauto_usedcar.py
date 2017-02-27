# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from PCauto.items import PCautoUsedCarItem
import math
import time
from PCauto import pipelines
from PCauto.mongodb import mongoservice


class PCautoUsedcarSpider(RedisSpider):
    name = 'PCauto_usedcar'
    api_url = 'https://www.guazi.com%s'
    pipeline = set([pipelines.UsedCarPipeline, ])


    def start_requests(self):
        config_urls = mongoservice.get_usedcar_url()
        for url in config_urls:
            yield Request(url, dont_filter=True, callback=self.get_vehicleTypes)
            yield Request(url, callback=self.get_url)

    def get_vehicleTypes(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        
        vehicles = soup.find('div', class_="list").find_all('li')
        for vehicle in vehicles:
            href = vehicle.find('p', class_='infoBox').find('a').get('href')
            yield Request(self.api_url % href, callback = self.get_usedcar)

        next_page = soup.find('div', class_='pageBox').find('a', class_='next')
        if next_page:
            next_page_url = next_page.get('href')
            yield Request(self.api_url % next_page_url, callback = self.get_vehicleTypes)


    def get_usedcar(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandbaojiaUrlItem()

        result['category'] = '二手车'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="crumbs")
        if place:
            text = place.get_text().strip().replace('\n','')
            result['address'] = text

        yield result


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandbaojiaUrlItem()

        result['category'] = '二手车'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text = place.get_text().strip().replace('\n','')
            result['address'] = text

        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for one minute to close the spider')
        time.sleep(60)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')

