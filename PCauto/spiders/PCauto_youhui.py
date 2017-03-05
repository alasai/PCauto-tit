# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBrandYouhuiItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoBrandYouhuiSpider(RedisSpider):
    name = 'PCauto_youhui'
    pipeline = set([pipelines.BrandYouhuiPipeline, ])

    def start_requests(self):
        config_urls = mongoservice.get_brand_youhui()
        for url in config_urls:
            yield Request(url, dont_filter=True, callback=self.getDealerByVehicleType)
            yield Request(url, callback=self.get_url)

    def getDealerByVehicleType(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        moreDealers = soup.find_all('div',class_='list-item-hd')
        for moreDealer in moreDealers:
            more_tag = moreDealer.find('span').find_next('a')
            if more_tag:
                href = more_tag.get('href')
                yield Request(href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandYouhuiItem()

        result['category'] = 'youhui'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position")
        if place:
            text = place.find('div',class_="pos-mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        position = soup.find('div', class_="wrap position")
        if position:
            text = position.find('span', class_="mark").get_text().strip().replace('\n', '').replace('\r', '')
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