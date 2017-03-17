# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoYouhuiItem
from PCauto import pipelines


class PCautoYouhuiSpider(RedisSpider):
    name = 'PCauto_youhui'
    youhui_url = 'http://price.pcauto.com.cn/youhui'
    api_url = 'http://price.pcauto.com.cn/youhui/r%s/'
    city_js_url = 'http://www.pcauto.com.cn/global/1603/intf8771.js'

    pipeline = set([pipelines.YouhuiPipeline, ])

    def start_requests(self):
        yield Request(self.city_js_url, callback=self.get_city)

    def get_city(self, response):
        body = response._body
        city_id_list = re.findall(r'"cityId":"(\d+)"', body)
        for city_id in city_id_list:
            yield Request(self.api_url % city_id, dont_filter=True, callback=self.get_page)
            yield Request(self.api_url % city_id, callback=self.get_url)

    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        list = soup.find('ul', class_='cont-list clearfix')
        if list:
            cars = list.find_all('li')
            for car in cars:
                href = car.find('p', class_='p1').find('a').get('href')
                yield Request(href, dont_filter=True, callback=self.getDealerByVehicleType)
                yield Request(href, callback=self.get_url)
        # find next page
        pager = soup.find('div', class_='page')
        if pager:
            next_page = pager.find('div', class_='pcauto_page').find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                yield Request(self.youhui_url + next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(self.youhui_url + next_page_url, callback=self.get_url)

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
        result = PCautoYouhuiItem()

        result['category'] = '优惠'
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