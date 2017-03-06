# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.mongodb import mongoservice
from PCauto.items import PCautoCommentItem
from PCauto import pipelines

class PCautoCommentSpider(RedisSpider):
    name = 'PCauto_comment'
    pipeline = set([pipelines.CommentPipeline, ])

    def start_requests(self):
        comment_urls = mongoservice.get_comment_url()
        for url in comment_urls:
            yield Request(url, dont_filter=True, callback=self.get_vehicleTypes)
            yield Request(url, callback=self.get_comment)


    def get_vehicleTypes(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        vehicleList = soup.find('div',id="cxList")
        if vehicleList:
            vehicles = vehicleList.find_all('div',class_='tr')
            for vehicle in vehicles:
                href = vehicle.find('a').get('href')
                yield Request(href, callback=self.get_comment)


    def get_comment(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')

        # find next page
        nav = soup.find('div',class_='main_nav_page')
        if nav:
            next_page = nav.find('a',class_='next')
            if next_page:
                href = next_page.get('href')
                yield Request(href, callback=self.get_comment)

        # save url
        result = PCautoCommentItem()
        result['category'] = 'comment'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
        position = soup.find('div',class_="position")
        if position:
            # chexi position (class = 'position')
            place = position.find('div',class_="pos-mark")
            if place:
                text = place.get_text().strip().replace('\n','').replace('\r','')
                result['address'] = text
            # chexing position (class = 'wrap position')
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