# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import re
import time
import json
from PCauto.items import PCautoBrandinfoItem
from PCauto.pipelines import BrandInfoPipeline


class PCautoBrandinfoSpider(RedisSpider):
    name = 'PCautos_brandinfo'
    get_url = 'http://price.pcauto.com.cn/cars/'
    pipeline = set([BrandInfoPipeline, ])

    def start_requests(self):
        yield Request(self.get_url, callback=self.get_brand_list)

    def get_brand_list(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        div_list = soup.find_all('div', class_='main clearfix')
        for div_info in div_list:
            dd_list = div_info.find_all('dd')
            for dd_info in dd_list:
                href_car = dd_info.find('p',class_='pTitle').find('a').get('href')
                yield Request('http://price.pcauto.com.cn' + href_car, callback=self.get_urls)

    def get_urls(self,response):
        soup = BeautifulSoup(response.body_as_unicode())
        result = PCautoBrandinfoItem()
        url=response.url
        tit=soup.find('title').get_text().strip()
        place=soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text=place.get_text().strip().replace('\n','')
            result['address'] = text
        result['category'] = '车系首页'
        result['tit']=tit
        result['url']=url
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


