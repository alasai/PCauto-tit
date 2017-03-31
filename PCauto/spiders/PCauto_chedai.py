# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoChedaiItem
from PCauto import pipelines
from PCauto.mongodb import mongoservice


class PCautoChedaiSpider(RedisSpider):
    name = 'PCauto_chedai'

    chedai_city_model_url = 'http://jr.pcauto.com.cn/choose/r%s/m%s-c0-s30-p24/'
    get_model_url = 'http://price.pcauto.com.cn/api/hcs/select/model_json_chooser?sgid=%s&status=1&type=2&callback=che'
    citys_url = 'http://jr.pcauto.com.cn/interface/outer/cityHasProduct.jsp'

    pipeline = set([pipelines.ChedaiPipeline, ])

    def start_requests(self):
        yield Request(self.citys_url, callback=self.get_citys)

    def get_citys(self,response):
        body = response._body
        city_id_list = re.findall(r'"mid":(\d+)', body)
        urls = mongoservice.get_fenqi_url()
        for url in urls:
            ma = re.search(r'sg(\d+)', url)
            sid = ma.group(1)
            for city_id in city_id_list:
                # # 拿到对应车型信息
                yield Request(self.get_model_url % sid, callback=self.get_model, meta={"cityId":city_id})
                # 记录下"车系-分期购车"的 url
                fenqi_city_url = url.replace('/choose/','/choose/r%s/')
                yield Request(fenqi_city_url % city_id, callback=self.get_url)


    def get_model(self,response):
        body = response._body
        mid_list = re.findall(r'"id":"(\d+)"', body)
        cityId = response.meta['cityId']
        for mid in mid_list:
            yield Request(self.chedai_city_model_url % (cityId,mid), callback=self.get_url)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoChedaiItem()

        result['category'] = '车贷'
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