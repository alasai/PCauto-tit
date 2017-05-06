# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
import math
from PCauto.items import PCautoDealerModelItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerModelSpider(RedisSpider):
    name = 'PCauto_dealer_model'
    pipeline = set([pipelines.DealerModelPipeline, ])
    root_url = 'http://price.pcauto.com.cn'
    # page_url = 'http://price.pcauto.com.cn/%s/p%d/model.html#model'

    def start_requests(self):
        urls = mongoservice.get_dealer_model()
        for url in urls:
            yield Request(url, dont_filter=True, callback=self.get_page)
            yield Request(url, callback=self.get_url)

    def get_page(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        model = soup.find('div', id='model').find('i').find('em').get_text()
        if model:
            # # catch dealer num
            # ma = re.search(r'.cn/(\d+)',response.url)
            # dealer_num = ma.group(1)

            # make page root url
            ma = re.search(r'(.*)/model', response.url)
            suffix = '/p%d/model.html#model'
            page_url = ma.group(1) + suffix

            # catch page amount
            ma = re.search(r'\d+', model)
            model_amount = ma.group()

            model_num = math.ceil(float(model_amount)/8)
            for page_num in range(1,int(model_num) + 1):
                yield Request(page_url % page_num, dont_filter=True, callback=self.get_car)
                yield Request(page_url % page_num, callback=self.get_url)
                # yield Request(self.page_url % (dealer_num,page_num), callback=self.get_car)
                # yield Request(self.page_url % (dealer_num,page_num), headers={
                #     'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"
                # },callback=self.get_car)

        # to find next page (can't find the pager)
        # pagelist = soup.find('div', id='pager').find('div',class_='pagelist')
        # if pagelist:
        #     next_page = pagelist.find('a', class_='current').find_next('a')
        #     if next_page:
        #         page_num = next_page.get_text()
        #         ma = re.search(r'.cn/(\d)',response.url)
        #         dealer_num = ma.group(1)
        #         yield Request(self.page_url % (dealer_num,page_num), callback=self.get_page)

    def get_car(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        car_list = soup.find('dl', class_="tjlist allchex clearfix").find_all('div',class_='autobox')
        for car in car_list:
            href = car.find('span').find('a').get('href')
            yield Request(href, dont_filter=True, callback=self.get_vehicleModel)
            yield Request(href, callback=self.get_url)


    def get_vehicleModel(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        # save the bottom price url of vehicle serie
        column_list = soup.find('dl', class_='clearfix btndls').find_all('a')
        for column in column_list:
            column_url = column.get('href')
            yield Request(self.root_url + column_url, callback=self.get_url)
        # get vehicle model
        vehicle_list = soup.find_all('dl', class_='chextab clearfix')
        for list in vehicle_list:
            vehicles = list.find_all('dd')
            for vehicle in vehicles:
                href = vehicle.find('div', class_='div01').find('a').get('href')
                yield Request(self.root_url + href, dont_filter=True, callback=self.get_price)
                yield Request(self.root_url + href, callback=self.get_url)

    def get_price(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        column_list = soup.find('dl', class_='clearfix btndls').find_all('a')
        for column in column_list:
            href = column.get('href')
            yield Request(href, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerModelItem()
        result['category'] = '经销商-车型展厅'
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