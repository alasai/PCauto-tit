# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import json
import re
from PCauto.mongodb import mongoservice
from PCauto import pipelines
from PCauto.items import PCautoDealerItem

class PCautoDealerSpider(RedisSpider):
    name = 'PCauto_dealer'
    index_page = 'http://price.pcauto.com.cn/shangjia/'
    root = 'http://price.pcauto.com.cn%s'

    pipeline = set([pipelines.DealerPipeline, ])


    def start_requests(self):
        yield Request(self.index_page,callback=self.get_brand)


    def get_brand(self,response):
        soup = BeautifulSoup(response.body_as_unicode(),'lxml')
        brand_tabs = soup.find_all('div',class_="tab-brand-list clearfix")
        for tab in brand_tabs[1:]:
            brands = tab.find_all('a')
            for brand in brands:
                href = brand.get('href')
                yield Request(href, dont_filter=True, callback=self.get_city)
                yield Request(href, callback=self.get_url)


    def get_city(self,response):
        soup = BeautifulSoup(response.body_as_unicode(),'lxml')
        citys = soup.find('div',class_="piList").find_all('span')
        for city in citys:
            href = city.find('a').get('href')
            if href != 'javascript:void(0)':
                yield Request(href, dont_filter=True, callback=self.get_page)
                yield Request(href, callback=self.get_url)


    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(),'lxml')
        list_body = soup.find('div',class_="listTb")
        if list_body:
            # save dealer url
            dealers = list_body.find('ul').find_all('li')
            for dealer in dealers:
                href = dealer.find('div',class_='divYSd').find('a').get('href')
                yield Request(href, dont_filter=True, callback=self.get_dealer)
                yield Request(href, callback=self.get_url)

            # get next page
            page_info = list_body.find('div',class_='pcauto_page')
            if page_info:
                next_page = page_info.find('a',class_='next')
                if next_page:
                    next_page_url = next_page.get('href')
                    yield Request(self.root % next_page_url, dont_filter=True, callback=self.get_page)
                    yield Request(self.root % next_page_url, callback=self.get_url)


    def get_dealer(self,response):
        soup = BeautifulSoup(response.body_as_unicode(),'lxml')

        # start save brandinfo,no longer crawl this page again.
        result_index = dict()
        result_index['category'] = '经销商-首页'
        result_index['url'] = response.url
        result_index['tit'] = soup.find('title').get_text().strip()
        put_result = json.dumps(dict(result_index), ensure_ascii=False, sort_keys=True, encoding='utf8').encode('utf8')
        save_result = json.loads(put_result)
        mongoservice.save_dealer_index(save_result)

        topnav = soup.find('div',class_="topnavs")
        if topnav:
            result = dict()
            navs = topnav.find('ul').find_all('li')
            for nav in navs[1:]:
                nav_a = nav.find('a')
                if nav_a:
                    url = nav_a.get('href')
                    ma = re.search(r'/(\d+)/(\w+)',url)
                    key = ma.group(2) + '_url'
                    result[key] = self.root % url

                # if url:
                #     if 'model' in url:
                #         result['model_url'] = self.root + url
                #     elif 'market' in url:
                #         result['market_url'] = self.root + url
                #     elif 'news' in url:
                #         result['news_url'] = self.root + url
                #     elif 'contact' in url:
                #         result['contact_url'] = self.root + url

            put_result = json.dumps(dict(result), ensure_ascii=False, sort_keys=True, encoding='utf8').encode('utf8')
            save_result = json.loads(put_result)
            mongoservice.save_dealer(save_result)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoDealerItem()

        result['category'] = '车系-经销商'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position")
        if place:
            text = place.find('span',class_="mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        yield result

    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for one minute to close the spider')
        time.sleep(30)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')






























