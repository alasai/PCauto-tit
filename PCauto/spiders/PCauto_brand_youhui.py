# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoYouhuiItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoBrandYouhuiSpider(RedisSpider):
    name = 'PCauto_brand_youhui'
    pipeline = set([pipelines.YouhuiBrandPipeline, ])

    city_js_url = 'http://www.pcauto.com.cn/global/1603/intf8771.js'

    def start_requests(self):
        yield Request(self.city_js_url, dont_filter=True, callback=self.get_city)

    def get_city(self, response):
        body = response._body
        city_id_list = re.findall(r'"cityId":"(\d+)"', body)
        for city_id in city_id_list:
            brand_youhui_urls = mongoservice.get_brand_youhui()
            for url in brand_youhui_urls:
                yield Request(url + 'r%s/' % city_id, callback=self.get_url)
            vehicle_youhui_urls = mongoservice.get_vehicleType()
            for v_url in vehicle_youhui_urls:
                yield Request(v_url + 'market/r%s/' % city_id, callback=self.get_url)

    # def start_requests(self):
    #     youhui_urls = mongoservice.get_brand_youhui()
    #     for url in youhui_urls:
    #         yield Request(url+'r2/', callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoYouhuiItem()

        result['category'] = '车系-优惠'
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