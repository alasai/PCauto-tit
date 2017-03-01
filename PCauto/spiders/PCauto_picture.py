# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBrandPictureUrlItem
from PCauto.pipelines import PicUrlPipeline
from PCauto.mongodb import mongoservice

class PCautoBrandPictureSpider(RedisSpider):
    name = 'PCauto_pic'
    api_url='http://price.pcauto.com.cn%s'
    pipeline = set([PicUrlPipeline, ])

    def start_requests(self):
        pic_urls = mongoservice.get_pic_url()
        for url in pic_urls:
            yield Request(url, dont_filter=True, callback=self.get_types)
            yield Request(url, callback=self.get_url)

    def get_types(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        box = soup.find_all('div',class_='mainBox').find('div',class_='tbA')
        if box:
            types = box.find_all('div',class_='tit-a clearfix')
            for type in types:
                href = type.find('a').get('href')
                yield Request(self.api_url % href, dont_filter=True, callback=self.get_page)
                yield Request(self.api_url % href,callback=self.get_url)
                
    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        list = soup.find_all('div',class_='mainBox').find('div',class_='tbA').find('ul',class_='ulPic ulPic-180 clearfix')
        if list:
            pictures = list.find_all('li')
            for pic in pictures:
                href = pic.find('a').get('href')
                yield Request(self.api_url % href,callback=self.get_url)
                
            # 下一页递归当前处理逻辑（列表存在时讨论分页才有意义）
            pages = soup.find('div',class_='page')
            if pages:
                next_page = pages.find('a', class_='next')
                if next_page:
                    next_page_url = next_page.get('href')
                    yield Request(self.api_url % next_page_url, callback = self.get_page)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandPictureUrlItem()

        result['category'] = '图片'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        # 测试图片 address 结构
        position = soup.find('div',class_="position positionPic")
        if position:
            text = position.find('span',class_="mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text
 
        topBar = soup.find('div',id = 'j-topBar')
        if topBar:
            text = topBar.find('div',class_="mark crumbs").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        yield result


    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for one minute to close the spider')
        time.sleep(60)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')
            
            