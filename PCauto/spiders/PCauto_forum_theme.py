# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from bs4 import BeautifulSoup
import time
import re
from PCauto.items import PCautoForumItem
from PCauto import pipelines


class PCautoThemeForumSpider(RedisSpider):
    name = 'PCauto_forum_theme'
    pipeline = set([pipelines.ForumPipeline, ])
    forum_root = 'http://bbs.pcauto.com.cn/'


    def start_requests(self):
        yield Request(self.forum_root, callback=self.get_forum_index)

    def get_forum_index(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        tabs = soup.find('div', class_='forumshow').find_all('div',class_='item')
        themelist = tabs[2].find_all('span')
        for theme in themelist:
            theme_forum_url = theme.find('a').get('href')
            yield Request(theme_forum_url, dont_filter=True, callback=self.get_forums)
            yield Request(theme_forum_url, callback=self.get_url)

    def get_forums(self, response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        forums = soup.find_all('span', class_="checkbox_title")
        for forum in forums:
            href = forum.find('a').get('href')
            yield Request(href, callback=self.get_url)

        # 下一页递归当前处理逻辑
        pager = soup.find('div', class_='pager')
        if pager:
            next_page = pager.find('a', class_='next')
            if next_page:
                next_page_url = next_page.get('href')
                yield Request(next_page_url, callback=self.get_forums)

    def get_url(self,response):
        soup = BeautifulSoup(response.body_as_unicode(), 'lxml')
        result = PCautoForumItem()

        result['category'] = '论坛'
        result['url'] = response.url
        result['tit'] = soup.find('title').get_text().strip()

        place = soup.find('div',class_="com-subHead add-link-gzcz BtmNoBor")
        if place:
            text_raw = place.find('div',class_="com-crumb").get_text().strip().replace('\n','').replace('\r','')
            ma = re.match(r'\S+',text_raw)
            text = ma.group()
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