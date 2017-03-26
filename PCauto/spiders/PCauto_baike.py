# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
import re
from PCauto import pipelines
from PCauto.items import PCautoBaikeItem

class PCautoBaikeSpider(RedisSpider):
    name = 'PCauto_baike'
    index_page = 'http://baike.pcauto.com.cn/'
    api_url = 'http://hj.pcauto.com.cn/article/listArticle.do?authorId=%s&pageNo=%d'
    article_url = 'http://hj.pcauto.com.cn/article/%s.html'

    pipeline = set([pipelines.BaikePipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_nav)


    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//ul[@id="nav"]//div[@class="word-box"]//li')
        for nav in nav_list:
            href = nav.xpath('./a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)

    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//ul[@class="data-list"]/li')
        for article in articles:
            href = article.xpath('./div[@class="data-tit"]/a/@href')[0]
            yield Request(href, callback=self.get_url)
        # next page
        page_info = model.xpath('//div[@class="pcauto_page"]')
        if page_info:
            next_page = page_info[0].xpath('./a[@class="next"]')
            if next_page:
                next_page_url = next_page[0].xpath('./@href')[0]
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)

    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoBaikeItem()
        result['category'] = '百科'
        result['url'] = response.url
        result['tit'] = model.xpath('//title')[0].text.strip()
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






























