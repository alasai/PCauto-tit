# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import json
import re
from PCauto.mongodb import mongoservice

class PCautoBrandListUrlSpider(RedisSpider):
    name="PCauto_start"
    get_brand_url = 'http://price.pcauto.com.cn/cars/'


    def start_requests(self):
        yield Request(self.get_brand_url, callback=self.get_brand_list)


    def get_brand_list(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        div_list = soup.find_all('div', class_='main clearfix')
        for div_info in div_list:
            href_brand = div_info.find('div',class_='dFix').find('a').get('href')
            bid_ma = re.search(r"nb(\d+)", href_brand)
            bid = bid_ma.group(1)
            dd_list = div_info.find_all('dd')
            for dd_info in dd_list:
                href_car = dd_info.find('p',class_='pTitle').find('a').get('href')
                cid_ma = re.search(r'sg(\d+)', href_car)
                cid = cid_ma.group(1)
                yield Request('http://price.pcauto.com.cn' + href_car, meta={'bid': bid, 'cid': cid}, callback=self.get_car_info)


    def get_car_info(self,response):
        info = response.body_as_unicode()
        soup = BeautifulSoup(info, 'lxml')

        # start save brandinfo,no longer crawl this page again.
        result_brandInfo = dict()
        result_brandInfo['category'] = '车系首页'
        result_brandInfo['url'] = response.url
        result_brandInfo['tit'] = soup.find('title').get_text().strip()
        place=soup.find('div',class_="position").find('div',class_="pos-mark")
        if place:
            text=place.get_text().strip().replace('\n','')
            result_brandInfo['address'] = text

        put_result = json.dumps(dict(result_brandInfo), ensure_ascii=False, sort_keys=True, encoding='utf8').encode('utf8')
        save_result = json.loads(put_result)
        mongoservice.save_brandInfo(save_result)

        # start save brand_list
        result = dict()
        nav_top = soup.find('div',id='JfixedTop')
        li_info = nav_top.find_all('li')
        config = li_info[1].find('a')
        if config:
            config_url =  config.get('href')
            result['config_url'] = config_url

        pic = li_info[2].find('a')
        if pic:
            pic_url = pic.get('href')
            result['pic_url'] = pic_url

        baojia = li_info[3].find('a')
        if baojia:
            baojia_url = baojia.get('href')
            result['baojia_url'] = baojia_url

        youhui = li_info[4].find('a')
        if youhui:
            youhui_url = youhui.get('href')
            result['youhui_url'] = youhui_url

        comment = li_info[5].find('a')
        if comment:
            comment_url = comment.get('href')
            result['comment_url'] = comment_url

        article = li_info[6].find('a')
        if article:
            article_url = article.get('href')
            result['article_url'] = article_url

        fenqi = li_info[7].find('a')
        if fenqi:
            fenqi_url = fenqi.get('href')
            result['fenqi_url'] = fenqi_url

        owner_price = li_info[8].find('a')
        if owner_price:
            owner_price_url = owner_price.get('href')
            result['owner_price_url'] = owner_price_url

        dealer = li_info[9].find('a')
        if dealer:
            dealer_url = dealer.get('href')
            result['dealer_url'] = dealer_url

        used_car = li_info[10].find('a')
        if used_car:
            used_car_url = used_car.get('href')
            result['used_car_url'] = used_car_url

        baoyang = li_info[11].find('a')
        if baoyang:
            baoyang_url = baoyang.get('href')
            result['baoyang_url'] = baoyang_url

        forum = li_info[12].find('a')
        if forum:
            forum_url = forum.get('href')
            result['forum_url'] = forum_url

        result['bid'] = response.meta['bid']
        result['cid'] = response.meta['cid']

        put_result = json.dumps(dict(result), ensure_ascii=False, sort_keys=True, encoding='utf8').encode('utf8')
        save_result = json.loads(put_result)
        mongoservice.save_brandlist(save_result)

    def spider_idle(self):
        """This function is to stop the spider"""
        req = self.next_requests()
        if req:
            self.schedule_next_requests()
        else:
            self.crawler.engine.close_spider(self, reason='finished')



