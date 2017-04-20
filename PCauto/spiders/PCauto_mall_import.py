# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from PCauto.items import PCautoMallImportItem
import time
import re
import math
from PCauto import pipelines


class PCautoMallImportSpider(RedisSpider):
    name = 'PCauto_mall_import'
    api_url = 'http://mall.pcauto.com.cn%s'
    mall_import = 'http://mall.pcauto.com.cn/import/nb/'

    vehicle_model_url = 'http://mall.pcauto.com.cn/import/model/pageModelGroup.do?pageNo=%s&pageSize=30&serialGroupId=%s'
    dealer_model_url = 'http://mall.pcauto.com.cn/import/model/pageModelGroupDetail.do?modelName=%s&serialGroupId=%s'

    mall_dealer_model = 'http://mall.pcauto.com.cn/import/m%s/'

    pipeline = set([pipelines.MallImportPipeline, ])

    def start_requests(self):
        yield Request(self.mall_import, callback=self.get_brand)

    def get_brand(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        brands = soup.find('div', class_='right').find_all('a')
        for brand in brands :
            href = brand.get('href')
            yield Request(self.api_url % href, dont_filter=True, callback=self.get_car)
            yield Request(self.api_url % href, callback=self.get_url)

    def get_car(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        cars = soup.find('div', id='Jlist').find_all('li')
        for car in cars:
            href = car.find('a').get('href')
            ma = re.search(r'sg(\d+)', href)
            serialGroupId = ma.group(1)
            yield Request(self.vehicle_model_url % (1,serialGroupId), dont_filter=True, callback=self.get_pages, meta={'serialGroupId':serialGroupId})
            yield Request(self.api_url % href, callback=self.get_url)

    def get_pages(self,response):
        serialGroupId = response.meta['serialGroupId']
        body = response._body
        ma = re.search(r'"total":(\d+)',body)
        total = ma.group(1)
        total_num = int(total)
        page_amount = math.ceil(total_num/30.0)
        # get all page data
        for page_num in range(1,int(page_amount) + 1):
            yield Request(self.vehicle_model_url % (page_num,serialGroupId), callback=self.get_vehicle_model, meta={'serialGroupId':serialGroupId})

    def get_vehicle_model(self,response):
        serialGroupId = response.meta['serialGroupId']
        body = response._body
        model_name_list = re.findall(r'"name":"(.*?)"', body)
        for name in model_name_list:
            yield Request(self.dealer_model_url % (name,serialGroupId), callback=self.get_dealer_model)

    def get_dealer_model(self,response):
        body = response._body
        dealer_modelId_list = re.findall(r'"dealerModelId":(\d+)', body)
        for modelId in dealer_modelId_list:
            yield Request(self.mall_dealer_model % modelId, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoMallImportItem()

        result['category'] = '汽车商城-平行进口车'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="fl")
        if place:
            text = place.get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

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

