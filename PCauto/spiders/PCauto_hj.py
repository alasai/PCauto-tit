# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from lxml import etree
import time
import re
from PCauto import pipelines
from PCauto.items import PCautoHangjiaItem

class PCautoHangjiaSpider(RedisSpider):
    name = 'PCauto_hangjia'
    index_page = 'http://hj.pcauto.com.cn/writer/'
    api_url = 'http://hj.pcauto.com.cn/article/listArticle.do?authorId=%s&pageNo=%d'
    article_url = 'http://hj.pcauto.com.cn/article/%s.html'

    pipeline = set([pipelines.HangjiaPipeline, ])

    def start_requests(self):
        yield Request(self.index_page, callback=self.get_hangjia)

    def get_hangjia(self,response):
        model = etree.HTML(response.body_as_unicode())
        hj_list = model.xpath('//div[@class="col-a"]//ul[@class="author-list"]/li')
        for hj in hj_list:
            href = hj.xpath('./div[@class="con"]/p[@class="name"]/a/@href')[0]
            yield Request(href, dont_filter=True, callback=self.get_page)
            yield Request(href, callback=self.get_url)
        # do in first page only
        cur_page_num = model.xpath('//div[@class="pager"]/span')[0].text
        if cur_page_num == '1':
            page_amount = model.xpath('//div[@class="pages"]//a[last()]')[0].text
            for page_num in range(2,int(page_amount)):
                page_url = self.index_page + str(page_num) + '/'
                yield Request(page_url, dont_filter=True, callback=self.get_hangjia)
                yield Request(page_url, callback=self.get_url)

    def get_page(self,response):
        model = etree.HTML(response.body_as_unicode())
        articles = model.xpath('//ul[@id="post-list"]/li')
        for article in articles:
            href = article.xpath('./div[@class="bd"]/h3[@class="tit"]/a/@href')[0]
            yield Request(href, callback=self.get_url)
        # get more articles
        author_data = model.xpath('//div[@class="author-data"]/p/i[1]')[0].text
        ma = re.search(r'\d+', author_data)
        articles_num = int(ma.group())
        if articles_num > 20:
            author_ma = re.search(r'\d+', response.url)
            author_id = author_ma.group()
            page_amount = articles_num / 20 + 1
            for page_num in range(2,page_amount + 1):
                page_url = self.api_url % (author_id,page_num)
                yield Request(page_url, callback=self.get_more_articles)

    def get_more_articles(self,response):
        body = response._body
        article_id_list = re.findall(r'"articleId":(\d+)',body)
        for article_id in article_id_list:
            yield Request(self.article_url % article_id, callback=self.get_url)

    def get_url(self,response):
        model = etree.HTML(response.body_as_unicode())
        result = PCautoHangjiaItem()
        result['category'] = '行家'
        result['url'] = response.url
        result['tit'] = model.xpath('//title')[0].text.strip()
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






























