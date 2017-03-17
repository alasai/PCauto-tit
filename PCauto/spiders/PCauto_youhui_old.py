# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoYouhuiItem
from PCauto.mongodb import mongoservice
from PCauto import pipelines


class PCautoYouhuiSpiderOld(RedisSpider):
    name = 'PCauto_youhui_old'
    pipeline = set([pipelines.YouhuiPipeline, ])

    def start_requests(self):
        config_urls = mongoservice.get_brand_youhui()
        for url in config_urls:
            yield Request(url, dont_filter=True, callback=self.getDealerByVehicleType)
            yield Request(url, callback=self.get_url)
            # yield Request(url, headers={
            #     'Host': 'price.pcauto.com.cn',
            #     'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
            #     'Cache-Control': 'max-age=0',
            #     'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     'X-Requested-With': 'XMLHttpRequest',
            #     'Accept-Encoding': 'gzip, deflate',
            #     'Accept-Language':"en-US,en;q=0.5",
            #     'Referer': url,
            #     'Connection': "keep-alive",
            #     'Upgrade - Insecure - Requests': "1",
            #     'Cookie': "locationddPro=%u4E0A%u6D77%u5E02; pcsuv=1487579952335.a.41795121; pcuvdata=lastAccessTime=1488789120223|visits=66; channel=7558; u=591fm4u7; c=591e3urj; redbaoss002=123; redbaoss002=123; pcLocate=%7B%22proCode%22%3A%22110000%22%2C%22pro%22%3A%22%E5%8C%97%E4%BA%AC%E5%B8%82%E7%9C%81%22%2C%22cityCode%22%3A%22110000%22%2C%22city%22%3A%22%E5%8C%97%E4%BA%AC%E5%B8%82%22%2C%22dataType%22%3A%22user%22%2C%22expires%22%3A1490019370791%7D; pcautoLocate=%7B%22proId%22%3A6%2C%22cityId%22%3A2%2C%22url%22%3A%22http%3A%2F%2Fwww.pcauto.com.cn%2Fqcbj%2Fbj%2F%22%2C%22dataTypeAuto%22%3A%22user%22%7D; favCar=%E5%A5%A5%E8%BF%AAA1_3746%7C%E5%A5%A5%E8%BF%AAA8L_7%7C%E5%A5%A5%E8%BF%AATT_8%7CLagonda_7719%7C%E5%A5%A5%E8%BF%AAA3_9550; u4ad=591hwr734; CMT4_IP_AREA=%u4E0A%u6D77%u5E02; captcha=e4cc2e59f6da042f40995b0e15aa19843613481337261494635538552; JSESSIONID=abcR_EaBJOfKD8Ev8ftQv; __PCautoPrice4s_area_id_=3-%u4E0A%u6D77-3; locationCity=%u4E0A%u6D77; PClocation=%u4E0A%u6D77"
            # }, dont_filter=True, callback=self.getDealerByVehicleType)

    def getDealerByVehicleType(self,response):
        soup = BeautifulSoup(response.body)
        moreDealers = soup.find_all('div',class_='list-item-hd')
        for moreDealer in moreDealers:
            more_tag = moreDealer.find('span').find_next('a')
            if more_tag:
                href = more_tag.get('href')
                yield Request(href,headers={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0"}, callback=self.get_url)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoYouhuiItem()

        result['category'] = '优惠'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="position")
        if place:
            text = place.find('div',class_="pos-mark").get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        position = soup.find('div', class_="wrap position")
        if position:
            text = position.find('span', class_="mark").get_text().strip().replace('\n', '').replace('\r', '')
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