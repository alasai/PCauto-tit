# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from lxml import etree
from PCauto.items import PCautoDealerModelItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerOtherSpider(RedisSpider):
    name = 'PCauto_dealer_other'
    pipeline = set([pipelines.DealerOtherPipeline, ])
    fenqi_url = 'http://jr.pcauto.com.cn/autofinance/commorders/order.jsp?sgid=%s#ad=8303'

    def start_requests(self):
        urls = mongoservice.get_dealer_model_other()
        for url in urls:
            yield Request(url, dont_filter=True, callback=self.get_nav)

    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//ul[@class="nav-area"]/li')
        for nav in nav_list:
            href = nav.xpath('./a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_vehicle_series)
            yield Request(href, callback=self.get_url)

    def get_vehicle_series(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        series = soup.find('div', class_='tab-ctrl').find_all('a')
        for serie in series[1:]:
            href = serie.get('href')
            yield Request(href, dont_filter=True, callback=self.get_price)
            yield Request(href, callback=self.get_url)

    def get_price(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        item = soup.find('div', class_='tab-item')
        if item:
            href = item.find('div', class_='btn-area clearfix').find('a').get('href')
            ma = re.search(r'sgid=(\d+)', href)
            fenqi_url = self.fenqi_url % ma.group(1)
            yield Request(fenqi_url, dont_filter=True, callback=self.get_other_column)
            yield Request(fenqi_url, callback=self.get_url)

    def get_other_column(self,response):
        model = etree.HTML(response.body_as_unicode())
        column_list = model.xpath('//div[@class="bmTab bmTab_add"]/a[@class="white"]')
        for column in column_list:
            href = column.xpath('./@href')[0]
            yield Request(href, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerModelItem()
        result['category'] = '经销商-询底价'
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