# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoDealerContactItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerContactSpider(RedisSpider):
    name = 'PCauto_dealer_contact'
    pipeline = set([pipelines.DealerContactPipeline, ])

    def start_requests(self):
        contact_urls = mongoservice.get_dealer_contact()
        for url in contact_urls:
            yield Request(url, dont_filter=True, callback=self.get_contacts)
            # yield Request(url, dont_filter=True,headers={
            #     'Host': "price.pcauto.com.cn",
            #     'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     # 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
            #     'User-Agent': "Mozilla / 5.0(Windows NT 6.1;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 56.0.2924.87Safari / 537.36",
            #     'Accept-Language': "zh-CN,zh;q=0.8",
            #     'Accept-Encoding': "gzip, deflate, sdch",
            #     'Connection': "keep-alive",
            #     'Cache-Control': "max-age=0",
            #     'Upgrade-Insecure-Requests': "1",
            #     'Referer': "http: // price.pcauto.com.cn / 89452 / news.html"
            # }, callback=self.get_contacts)
            yield Request(url, callback=self.get_url)

    def get_contacts(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        tab_list = soup.find('div', class_="ctltag")
        if tab_list:
            tabs = tab_list.find_all('a')
            for tab in tabs[1:]:
                href = tab.get('href')
                yield Request(href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerContactItem()
        result['category'] = '经销商-联系我们'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
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