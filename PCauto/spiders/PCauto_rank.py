# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
import re
from PCauto import pipelines
from PCauto.items import PCautoRankItem

class PCautoRankSpider(RedisSpider):
    name = 'PCauto_rank'
    index_page = 'http://price.pcauto.com.cn/top/r3/'
    # index_page = 'http://price.pcauto.com.cn/top/hot/s1-t1.html'
    api_url = 'http://price.pcauto.com.cn%s'

    pipeline = set([pipelines.RankPipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_left_nav)

    def get_left_nav(self,response):
        model = etree.HTML(response.body_as_unicode())
        nav_list = model.xpath('//div[@id="leftNav"]/ul[@class="pb200"]/li')
        for index,nav in enumerate(nav_list[1:]):
            sub_nav_list = nav.xpath('.//a[@class="dd "]')
            for sub_nav in sub_nav_list:
                href = self.api_url % sub_nav.xpath('./@href')[0]
                if index == 1:
                    yield Request(href, dont_filter=True, callback=self.get_sales_rank)
                else:
                    yield Request(href, dont_filter=True, callback=self.get_other_rank)
                yield Request(href, callback=self.get_url)


    def get_sales_rank(self,response):
        # //div[@class="sel-date-box"]
        model = etree.HTML(response.body_as_unicode())
        year_list = model.xpath('//ul[@class="ul-yy"]/li')
        mon_list = model.xpath('//ul[@class="ul-mon"]/li')
        # get other month pages
        for year in year_list:
            year_num = year.text
            for mon in mon_list:
                ma = re.search(r'\d+', mon.text)
                mon_num = ma.group()
                # make new url
                rep_str = '-y' + year_num + '-m' + mon_num + '.html'
                href = re.sub(r'.html', rep_str, response.url)
                yield Request(href, callback=self.get_url)


    def get_other_rank(self,response):
        model = etree.HTML(response.body_as_unicode())
        order_list = model.xpath('//ul[@class="list-a"]/li')
        for order in order_list:
            href = order.xpath('./a/@href')[0]
            ma = re.match(r'http://.*', href)
            # jingpin
            if not ma:
                href = self.api_url % href
            yield Request(href, callback=self.get_url)
        # next page
        page_info = model.xpath('//div[@class="pcauto_page"]')
        if page_info:
            next_page = page_info[0].xpath('./a[@class="next"]')
            if next_page:
                next_page_url = self.api_url % next_page[0].xpath('./@href')[0]
                yield Request(next_page_url, dont_filter=True, callback=self.get_other_rank)
                yield Request(next_page_url, callback=self.get_url)


    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoRankItem()

        result['category'] = '汽车排行榜'
        result['url'] = response.url
        result['tit'] = model.xpath('//title')[0].text.strip()
        # paihang
        position = model.xpath('//div[@class="position"]/span[@class="mark"]')
        if position:
            text = position[0].xpath('string()')
            result['address'] = text
        # jingpin
        place = model.xpath('//div[@class="position clearfix"]/div[@class="mark"]')
        if place:
            text = place[0].xpath('string()')
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






























