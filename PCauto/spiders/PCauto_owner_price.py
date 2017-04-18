# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.mongodb import mongoservice
from PCauto.items import PCautoOwnerPriceItem
from PCauto import pipelines

class PCautoOwnerPriceSpider(RedisSpider):
    name = 'PCauto_owner_price'
    pipeline = set([pipelines.OwnerPricePipeline, ])

    def start_requests(self):
        owner_price_urls = mongoservice.get_owner_price()
        for url in owner_price_urls:
            # yield Request(url, dont_filter=True, headers={
            #     'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            # },callback=self.get_sales_column)
            yield Request(url, dont_filter=True, callback=self.get_sales_column)


    def get_sales_column(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        columns = soup.find('div', class_='col-m-2').find('span').find_all('a')
        for column in columns :
            href = column.get('href')
            yield Request(href, dont_filter=True, callback=self.get_vehicleTypes)
            yield Request(href, callback=self.get_url)


    def get_vehicleTypes(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        vehicles = soup.find_all('div',class_='tr')
        for vehicle in vehicles:
            href = vehicle.find('span',class_='td1').find('a').get('href')
            yield Request(href, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')

        # save url
        result = PCautoOwnerPriceItem()
        result['category'] = '车主价格'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        position = soup.find('div',class_="position")
        if position:
            # 车系 position (class = 'position')
            place = position.find('div',class_="pos-mark")
            if place:
                text = place.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
            # 车型 position (class = 'wrap position')
            mark = position.find('span',class_="mark")
            if mark:
                text = mark.get_text().strip().replace('\n','').replace('\r','')
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