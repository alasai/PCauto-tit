# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
from PCauto import pipelines
from PCauto.items import PCautoKejiItem

class PCautoKejiSpider(RedisSpider):
    name = 'PCauto_keji'
    index_page = 'http://autotech.pcauto.com.cn/'

    pipeline = set([pipelines.KejiPipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_nav)

    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//ul[@class="hed_nav"]/li')
        for nav in nav_list[1:]:
            href = nav.xpath('./a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)


    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//div[@class="list-wrap"]//li')
        for article in articles:
            href = article.xpath('./dl/dt/a/@href')[0]
            if href != 'null':
                yield Request(href, callback=self.get_url)
            else:
                print 'error article: ' + article.xpath('./dl/dt/a')[0].text

        next_page = model.xpath('//div[@id="page"]/a[@class="next"]')
        if next_page:
            next_page_url = next_page[0].xpath('./@href')[0]
            yield Request(next_page_url, dont_filter=True, callback=self.get_page)
            yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoKejiItem()
        result['category'] = '科技'
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






























