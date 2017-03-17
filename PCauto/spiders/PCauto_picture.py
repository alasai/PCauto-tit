# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBrandPictureUrlItem
from PCauto.pipelines import PicUrlPipeline
from PCauto.mongodb import mongoservice

class PCautoBrandPictureSpider(RedisSpider):
    name = 'PCauto_pic'
    api_url='http://price.pcauto.com.cn%s'
    pipeline = set([PicUrlPipeline, ])

    def start_requests(self):
        pic_urls = mongoservice.get_pic_url()
        for url in pic_urls:
            yield Request(url, dont_filter=True, callback=self.get_year)
            yield Request(url, callback=self.get_url)


    def get_year(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        # 年款
        labels = soup.find('div', class_='row j-box-open').find_all('span', class_='ul-label')
        for label in labels:
            href = label.find('a').get('href')
            yield Request(self.api_url % href, callback=self.get_url)
        # 在售车型
        boxes = soup.find('div', class_='row j-box-open').find_all('div', class_='ul-box')
        for box in boxes:
            vehicles = box.find_all('li')
            for vehicle in vehicles:
                href = vehicle.find('a').get('href')
                yield Request(self.api_url % href, dont_filter=True, callback=self.get_types)
                yield Request(self.api_url % href, callback=self.get_url)
        # 停售车型
        vehicle_discontinued = soup.find('div', class_='row j-box-open').find('div', class_='subMark flex-btn').find('a')
        if vehicle_discontinued:
            url = vehicle_discontinued.get('href')
            yield Request(self.api_url % url, dont_filter=True, callback=self.get_vehicle_discontinued)
            yield Request(self.api_url % url, callback=self.get_url)
        # 图解 组图 车展
        types = soup.find('div', class_='row bdn').find_all('li', class_=False)
        for  idx,val in enumerate(types):
            type_url = val.find('a').get('href')
            yield Request(self.api_url % type_url, callback=self.get_url)
            # 对车展做进一步挖掘
            if idx == types.__len__() - 1:
                yield Request(self.api_url % type_url, callback=self.get_items)


    def get_vehicle_discontinued(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        # 年款
        labels = soup.find('div', class_='row j-box-open').find_all('span', class_='ul-label')
        for label in labels:
            href = label.find('a').get('href')
            yield Request(self.api_url % href, callback=self.get_url)
        # 在售车型
        boxes = soup.find('div', class_='row j-box-open').find_all('div', class_='ul-box')
        for box in boxes:
            vehicles = box.find_all('li')
            for vehicle in vehicles:
                href = vehicle.find('a').get('href')
                yield Request(self.api_url % href, dont_filter=True, callback=self.get_types)
                yield Request(self.api_url % href, callback=self.get_url)


    def get_types(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        types = soup.find('div',class_='row bdn').find_all('li', class_=True)
        for type in types:
            dds = type.find('dl').find_all('dd')
            for dd in dds:
                type_url = dd.find('a').get('href')
                yield Request(self.api_url % type_url, dont_filter=True, callback=self.get_page)
                yield Request(self.api_url % type_url, callback=self.get_url)


    def get_items(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        items = soup.find('div', class_='bd bdn').find('dd', class_='item-a clearfix').find_all('a')
        for item in items[-5:]:
            href = item.get('href')
            yield Request(self.api_url % href, callback=self.get_item_list)


    def get_item_list(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        list_url = soup.find('div',class_='ft clearfix ft-fix').find('a').get('href')
        yield Request(self.api_url % list_url, callback=self.get_item_page)


    def get_item_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        pictures = soup.find('ul', id='JList').find_all('li')
        for pic in pictures:
            href = pic.find('a').get('href')
            yield Request(self.api_url % href, callback=self.get_url)

        # 下一页递归当前处理逻辑
        pages = soup.find('div', class_='pcauto_page')
        if pages:
            next_page = pages.find('a', class_='next')
            if next_page:
                next_page_url = '/' + next_page.get('href')
                yield Request(self.api_url % next_page_url, dont_filter=True, callback=self.get_item_page)
                yield Request(self.api_url % next_page_url, callback=self.get_url)


    def get_page(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        list = soup.find('div',class_='tbA').find('ul',class_='ulPic ulPic-180 clearfix')
        if list:
            pictures = list.find_all('li')
            for pic in pictures:
                href = pic.find('a').get('href')
                yield Request(self.api_url % href,callback=self.get_url)
                
            # 下一页递归当前处理逻辑（列表存在时讨论分页才有意义）
            pages = soup.find('div',class_='page')
            if pages:
                next_page = pages.find('a', class_='next')
                if next_page:
                    next_page_url = next_page.get('href')
                    yield Request(self.api_url % next_page_url, dont_filter=True, callback = self.get_page)
                    yield Request(self.api_url % next_page_url, callback=self.get_url)


    def get_url(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandPictureUrlItem()

        result['category'] = '图片'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        # 测试图片 address 结构
        position = soup.find('div', class_="position positionPic")
        if position:
            text = position.find('span', class_="mark").get_text().strip().replace('\n', '').replace('\r', '')
            result['address'] = text

        topBar = soup.find('div', id='j-topBar')
        if topBar:
            text = topBar.find('div', class_="mark crumbs").get_text().strip().replace('\n', '').replace('\r', '')
            result['address'] = text

        yield result

    # def get_types_old(self,response):
    #     soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
    #     types = soup.find('div',class_='tbA').find_all('div',class_='tit-a clearfix')
    #     for type in types:
    #         more_info = type.find('a')
    #         if more_info:
    #             more_url = more_info.get('href')
    #             yield Request(self.api_url % more_url, dont_filter=True, callback=self.get_page)
    #             yield Request(self.api_url % more_url, callback=self.get_url)
    #         else:
    #             list = type.find_next_sibling('ul')
    #             if list:
    #                 pictures = list.find_all('li')
    #                 for pic in pictures:
    #                     href = pic.find('a').get('href')
    #                     yield Request(self.api_url % href, callback=self.get_url)



    def spider_idle(self):
        """This function is to stop the spider"""
        self.logger.info('the queue is empty, wait for one minute to close the spider')
        time.sleep(10)
        req = self.next_requests()

        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')
            
            