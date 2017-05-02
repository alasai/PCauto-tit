# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
from PCauto.items import PCautoBrandArticleItem
from PCauto.pipelines import ArticlePipeline
from PCauto.mongodb import mongoservice

class PCautoArticleSpider(RedisSpider):
    name = 'PCauto_article'
    api_url = 'http://price.pcauto.com.cn%s'
    pipeline = set([ArticlePipeline, ])

    # test_urls = ['http://price.pcauto.com.cn/sg3543/article/p25.html','http://price.pcauto.com.cn/sg8238/article/p1.html']

    def start_requests(self):
        article_urls = mongoservice.get_article_url()
        for url in article_urls:
            yield Request(url, dont_filter=True, callback=self.get_articles)
            yield Request(url, callback=self.get_url)
        # for url in self.test_urls:
        #     yield Request(url, dont_filter=True, callback=self.get_articles)
        #     yield Request(url, callback=self.get_url)

    def get_articles(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        articles = soup.find_all('div', class_="tab-item")
        if articles:
            for article in articles:
                href = article.find('div', class_='txt').find('div', class_='tit').find('a').get('href')
                yield Request(href, callback = self.get_url)
    
            # 下一页递归当前处理逻辑
            pages = soup.find('div',class_='page')
            if pages:
                next_page = pages.find('a', class_='next')
                if next_page:
                    next_page_url = next_page.get('href')
                    yield Request(self.api_url % next_page_url, callback = self.get_articles)


    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoBrandArticleItem()

        result['category'] = '文章'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        # 车系页标签
        place = soup.find('div',class_="position")
        if place:
            text = place.get_text().strip().replace('\n','').replace('\r','')
            result['address'] = text

        # 文章页标签
        guide = soup.find('div',class_="guide")
        if guide:
            crumbs = guide.find('div',class_="crumbs")
            if crumbs:
                text = crumbs.get_text().strip().replace('\n','').replace('\r','')
            else:
                text = guide.find('span',class_="mark").get_text().strip().replace('\n','').replace('\r','')

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


















