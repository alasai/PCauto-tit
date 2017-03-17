# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoVideoItem
from PCauto import pipelines


class PCautoVideoSpider(RedisSpider):
    name = 'PCauto_video'
    root = 'http://price.pcauto.com.cn%s'
    bid_url = 'http://price.pcauto.com.cn/index/js/5_5/treedata-vn-html.js'
    sid_url = 'http://price.pcauto.com.cn/index/js/5_5/treedata-vn-%s.js'

    pipeline = set([pipelines.VideoPipeline, ])

    def start_requests(self):
        yield Request(self.bid_url,callback=self.get_brand)

    def get_brand(self,response):
        body = response._body
        brand_id_list = re.findall(r'pictext_a_(\d+)"', body)
        for bid in brand_id_list:
            yield Request(self.sid_url % bid, callback=self.get_car)

    def get_car(self,response):
        body = response._body
        ma = re.search(r'brandList_\d*=\'(.+)\';', body)
        car_page_str = ma.group(1)
        soup = BeautifulSoup(car_page_str,'lxml')
        cars = soup.find_all('li',id=True)
        for car in cars:
            href = car.find('a').get('href')
            # if not normal url,add the prefix
            ma_href = re.match(r'^http.*',href)
            if not ma_href:
                href = self.root % href
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)


    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        videos = soup.find('ul', class_='expPicC').find_all('li')
        for video in videos:
            href = video.find('i', class_='iTitle').find('a').get('href')
            yield Request(href, callback=self.get_url)
        # next page
        pager = soup.find('div', id='pagerdiv')
        if pager:
            next_page = pager.find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                yield Request(self.root % next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(self.root % next_page_url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoVideoItem()

        result['category'] = '车系-视频'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        # chexi
        place = soup.find('div',class_="position positionPic")
        if place:
            text = place.find('span',class_="mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text
        # video
        breadcrumb = soup.find('div', class_='breadcrumb')
        if breadcrumb:
            text = breadcrumb.get_text().strip().replace('\n','').replace('\r','')
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