# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
from PCauto.items import PCautoUsedCarItem
import time
from PCauto import pipelines
from PCauto.mongodb import mongoservice


class PCautoUsedcarSpider(RedisSpider):
    name = 'PCauto_usedcar'
    api_url = 'https://www.guazi.com%s'
    guazi_url = 'https://www.guazi.com/www/buy/'
    guazi_headers = {
        "Host": "www.guazi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.guazi.com/www/buy/",
        "Cookie": "ganji_uuid=6750379362540425962463; uuid=68b9d67b-b2fd-47d4-8496-774248115478; 68b9d67b-b2fd-47d4-8496-774248115478_views=66; ea472486-cb30-4211-d9bc-449fe56b5205_views=3; gzCityDomain=www; cainfo=%7B%22ca_s%22%3A%22pz_baidu%22%2C%22ca_n%22%3A%22tbmkbturl%22%2C%22platform%22%3A%221%22%2C%22version%22%3A%221%22%2C%22ca_i%22%3A%22-%22%2C%22ca_medium%22%3A%22-%22%2C%22ca_term%22%3A%22-%22%2C%22ca_content%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22keyword%22%3A%22-%22%2C%22ca_keywordid%22%3A%22-%22%2C%22scode%22%3A%2210103000312%22%7D; Hm_lvt_e6e64ec34653ff98b12aab73ad895002=1492667685,1493966275; cityDomain=www; clueSourceCode=10103000312%2300; GANJISESSID=9e93a0b28a75f7af307dfeb7b6f71b52; sessionid=c4d82283-0c8a-4440-e6c4-e37477363421; c4d82283-0c8a-4440-e6c4-e37477363421_views=63; lg=1; _gl_tracker=%7B%22ca_source%22%3A%22-%22%2C%22ca_name%22%3A%22-%22%2C%22ca_kw%22%3A%22-%22%2C%22ca_id%22%3A%22-%22%2C%22ca_s%22%3A%22pz_baidu%22%2C%22ca_n%22%3A%22tbmkbturl%22%2C%22ca_i%22%3A%22-%22%2C%22sid%22%3A52674874343%7D; Hm_lpvt_e6e64ec34653ff98b12aab73ad895002=1493970860"
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }

    pipeline = set([pipelines.UsedCarPipeline, ])


    def start_requests(self):
        # usedcar_urls = mongoservice.get_usedcar_url()
        # for url in usedcar_urls:
        #     yield Request(url, callback=self.get_url)
        # yield Request(self.guazi_url, callback=self.get_page)
        yield Request(self.guazi_url, callback=self.get_brand)
        # yield Request(self.guazi_url, headers=self.guazi_headers, callback=self.get_page)

    def get_brand(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        brand_list = soup.find('ul',class_='o-b-list').find_all('a')
        for brand in brand_list:
            href = brand.get('href')
            yield Request(self.api_url % href, dont_filter=True, callback=self.get_car_series)
            yield Request(self.api_url % href, callback=self.get_url)

    def get_car_series(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        series_list = soup.find('dd',class_='clickTagWidget').find_all('a')
        for serie in series_list[1:]:
            href = serie.get('href')
            yield Request(self.api_url % href, dont_filter=True, callback=self.get_page)
            yield Request(self.api_url % href, callback=self.get_url)

    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        car_list = soup.find('div', class_='list').find('ul',class_='list-bigimg clearfix lazyLoadV2').find_all('li')
        for car in car_list:
            href = car.find('p', class_='infoBox').find('a').get('href')
            yield Request(self.api_url % href, callback=self.get_url)
            # yield Request(self.api_url % href, headers=self.guazi_headers, callback=self.get_url)

        next_page = soup.find('div', class_='pageBox').find('a', class_='next')
        if next_page:
            next_page_url = next_page.get('href')
            yield Request(self.api_url % next_page_url, callback = self.get_page)
            # yield Request(self.api_url % next_page_url, headers=self.guazi_headers, callback = self.get_page)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoUsedCarItem()

        result['category'] = '二手车'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        guazi_position = soup.find('div',class_="crumbs")
        if guazi_position:
            text = guazi_position.get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        place = soup.find('div',class_="position")
        if place:
            text = place.find('div',class_="pos-mark").get_text().strip().replace('\n','').replace('\r','')
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

