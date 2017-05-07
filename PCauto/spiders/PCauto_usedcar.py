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
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    pipeline = set([pipelines.UsedCarPipeline, ])


    def start_requests(self):
        usedcar_urls = mongoservice.get_usedcar_url()
        for url in usedcar_urls:
            yield Request(url, callback=self.get_url)
        # yield Request(self.guazi_url, headers=self.guazi_headers, callback=self.get_page)
        # yield Request(self.guazi_url, callback=self.get_page)
        yield Request(self.guazi_url, callback=self.get_brand)

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
            # yield Request(self.api_url % href, headers=self.guazi_headers, callback=self.get_url)
            yield Request(self.api_url % href, callback=self.get_url)

        next_page = soup.find('div', class_='pageBox').find('a', class_='next')
        if next_page:
            next_page_url = next_page.get('href')
            # yield Request(self.api_url % next_page_url, headers=self.guazi_headers, callback = self.get_page)
            yield Request(self.api_url % next_page_url, callback = self.get_page)

    #
    # def get_vehicleList(self,response):
    #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
    #     guazi_url = soup.find('iframe').get('src')
    #     yield Request(guazi_url, callback=self.get_vehicleTypes)
    #
    #
    # def get_vehicleTypes(self,response):
    #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
    #
    #     list = soup.find('div', class_="list")
    #     vehicles = list.find_all('li')
    #     for vehicle in vehicles:
    #         href = vehicle.find('p', class_='infoBox').find('a').get('href')
    #         yield Request(self.api_url % href, callback = self.get_usedcar)
    #
    #     next_page = soup.find('div', class_='pageBox').find('a', class_='next')
    #     if next_page:
    #         next_page_url = next_page.get('href')
    #         yield Request(self.api_url % next_page_url, callback = self.get_vehicleTypes)
    #
    #

    # def get_usedcar(self,response):
    #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
    #     result = PCautoUsedCarItem()
    #
    #     result['category'] = '二手车'
    #     result['url'] = response.url
    #     result['tit'] = soup.find('title').get_text().strip()
    #
    #     place = soup.find('div',class_="crumbs")
    #     if place:
    #         text = place.get_text().strip().replace('\n','')
    #         result['address'] = text
    #
    #     yield result


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

