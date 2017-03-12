# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoDealerNewsItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoDealerNewsSpider(RedisSpider):
    name = 'PCauto_dealer_news'
    pipeline = set([pipelines.DealerNewsPipeline, ])
    root_url = 'http://price.pcauto.com.cn'

    def start_requests(self):
        urls = mongoservice.get_dealer_news()
        for url in urls:
            # yield Request(url, dont_filter=True, callback=self.get_news)
            yield Request(url, dont_filter=True, headers={
                'Host': "price.pcauto.com.cn",
                'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
                # 'Accept-Language': "en-US,en;q=0.5",
                # 'Accept-Encoding': "gzip, deflate",
                # 'Referer': "http://price.pcauto.com.cn/89452/news.html",
                # 'Connection': "keep-alive",
                # 'Cache-Control': "max-age=0",
                # 'Upgrade-Insecure-Requests': "1"
            }, callback=self.get_news)
            yield Request(url, callback=self.get_url)

    def get_news(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        news_list = soup.find('ul', class_='zxlist clearfix').find_all('li')
        for news in news_list:
            href = news.find('p').find('a').get('href')
            yield Request(self.root_url + href, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerNewsItem()
        result['category'] = '经销商-店铺资讯'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()
        yield result

    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for half minute to close the spider')
        time.sleep(10)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')