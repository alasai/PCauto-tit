# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
import re
from PCauto import pipelines
from PCauto.items import PCautoProductItem

class PCautoProductSpider(RedisSpider):
    name = 'PCauto_product'
    index_page = 'http://product.pcauto.com.cn/'
    api_page = 'http://product.pcauto.com.cn%s'

    pipeline = set([pipelines.ProductPipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_nav)

    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//div[@class="bttitlle"]/a')
        for nav in nav_list[1:]:
            href = self.api_page % nav.xpath('./@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)

    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//div[@class="list_dt"]')
        for article in articles:
            href = article.xpath('./a/@href')[0]
            ma = re.match(r'http://.*', href)
            if not ma:
                href = self.api_page % href
            yield Request(href, callback=self.get_url)

        page_info = model.xpath('//div[@class="pcauto_page"]')
        if page_info:
            next_page = page_info[0].xpath('.//a[@class="next"]')
            if next_page:
                next_page_url = self.api_page % next_page[0].xpath('./@href')[0]
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)

    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoProductItem()

        result['category'] = '用品库'
        result['url'] = response.url
        result['tit'] = model.xpath('//title')[0].text.strip()
        # nav
        position = model.xpath('//div[@class="position"]/span[@class="mark"]')
        if position:
            text = position[0].xpath('string()')
            result['address'] = text
        # product
        crumbs = model.xpath('//div[@class="crumbs"]/span[@class="mark"]')
        if crumbs:
            text = crumbs[0].xpath('string()')
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






























