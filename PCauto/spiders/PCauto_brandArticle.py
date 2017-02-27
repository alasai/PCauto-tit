# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBrandArticleItem
from PCauto.pipelines import ArticlePipeline
from PCauto.mongodb import mongoservice

class PCautoArticleSpider(RedisSpider):
    name = 'PCauto_newcar'
    api_url='http://info.xcar.com.cn/'
    pipeline = set([ArticlePipeline, ])


    def start_requests(self):
        article_urls = mongoservice.get_article_url()
        for url in article_urls:
            yield Request(self.api_url, dont_filter=True, callback=self.get_articles)
            yield Request(url, callback=self.get_url)

    def get_articles(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')

        list = soup.find('div', class_="list")
        vehicles = list.find_all('li')
        for vehicle in vehicles:
            href = vehicle.find('p', class_='infoBox').find('a').get('href')
            yield Request(self.api_url % href, callback = self.get_url)

        next_page = soup.find('div', class_='pageBox').find('a', class_='next')
        if next_page:
            next_page_url = next_page.get('href')
            yield Request(self.api_url % next_page_url, callback = self.get_articles)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandArticleItem()

        result['category'] = 'wenzhang'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text = place.get_text().strip().replace('\n','')
            result['address'] = text

        yield result


    def get_article(self,response):
        soup = BeautifulSoup(response.body_as_unicode())
        result = PCautoBrandArticleItem()
        url=response.url
        tit=soup.find('title').get_text().strip()
        current_path=soup.find('div',class_="current_path")
        if current_path:
            p_info=current_path.find('p')
            if p_info:
                text=p_info.get_text().strip()
                add = text.split('：')
                result['address'] = add[1][:-2]

            p1=current_path.find('div',class_="p1")
            if p1:
                text = p1.get_text().strip()
                address = text.split('：')
                result['address'] = address[1]
        place = soup.find('div', class_="place")
        if place:
            text = place.get_text().strip()
            add = text.split(':')
            result['address'] = add[1]
        result['category'] = '新车频道'
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


















