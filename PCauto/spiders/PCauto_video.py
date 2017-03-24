# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoVideoItem
from PCauto import pipelines

class PCautoVideoSpider(RedisSpider):
    name = 'PCauto_video'

    video_index = 'http://pcauto.pcvideo.com.cn/'

    pipeline = set([pipelines.VideoPipeline, ])

    def start_requests(self):
        yield Request(self.video_index, callback=self.get_nav)

    def get_nav(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        navs = soup.find('ul', class_='clearfix inner').find_all('li')
        # normal
        for nav in navs[3:-1]:
            href = nav.find('a').get('href')
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)
        # self made
        yuanchuang_navs = soup.find('ul', class_='clearfix inner').find('li', class_='prdlit').find_all('dd')
        for sub_nav in yuanchuang_navs:
            sub_href = sub_nav.find('a').get('href')
            yield Request(sub_href, dont_filter=True, callback=self.get_page)
            yield Request(sub_href, callback=self.get_url)
        # daren
        daren_href = navs[-1].find('a').get('href')
        yield Request(daren_href, callback=self.get_subscription)

    def get_subscription(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        lis = soup.find('div', class_='condr').find_all('li')
        for li in lis:
            href = li.find('a').get('href')
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)


    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        videos = soup.find('ul', class_='list clearfix').find_all('li')
        for video in videos:
            href = video.find('a').get('href')
            yield Request(href, callback=self.get_url)
        # next page
        pager = soup.find('div', class_='pages')
        if pager:
            next_page = pager.find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoVideoItem()

        result['category'] = '视频'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        # nav
        place = soup.find('div',class_="mtts")
        if place:
            text = place.get_text().strip().replace('\n','').replace('\r','')
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