# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
from PCauto import pipelines
from PCauto.items import PCautoMotoSportItem

class PCautoMotoSportSpider(RedisSpider):
    name = 'PCauto_motosport'
    index_page = 'http://www.pcauto.com.cn/motosport/'

    pipeline = set([pipelines.MotoSportPipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_nav)

    def get_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//ul[@id="nav"]/li')
        for nav in nav_list[1:]:
            href = nav.xpath('./a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)


    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//div[@class="box list"]//div[@class="pic-txt clearfix"]')
        for article in articles:
            href = article.xpath('./div[@class="txt"]//p[@class="tit blue"]/a/@href')[0]
            yield Request(href, callback=self.get_url)

        page_info = model.xpath('//div[@class="pcauto_page"]')
        if page_info:
            next_page = page_info[0].xpath('./a[@class="next"]')
            if next_page:
                next_page_url = next_page[0].xpath('./@href')[0]
                yield Request(next_page_url, dont_filter=True, callback=self.get_page)
                yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoMotoSportItem()

        result['category'] = '赛事'
        result['url'] = response.url
        result['tit'] = model.xpath('//title')[0].text.strip()

        place = model.xpath('//div[@class="guide"]')
        # nav and aiticle
        if place:
            mark = place[0].xpath('./span[@class="mark"]')
            if mark:
                text = mark[0].xpath('string()')
                result['address'] = text
            crumbs = place[0].xpath('./div[@class="crumbs"]')
            if crumbs:
                text = crumbs[0].xpath('string()')
                result['address'] = text
        # video(none)
        breadcrumb = model.xpath('//div[@class="breadcrumb"]')
        if breadcrumb:
            text = breadcrumb[0].xpath('string()')
            result['address'] = text
        # forum
        com_crumb = model.xpath('//div[@class="com-crumb"]')
        if com_crumb:
            text = com_crumb[0].xpath('string()')
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






























