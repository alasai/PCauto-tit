#-*-coding:utf-8-*-

import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
import logging

logger = logging.getLogger('HttpStatusLogger')

# class RotateUserAgentMiddleware(UserAgentMiddleware):
class RotateUserAgentMiddleware(object):
    def __init__(self, user_agents='Bruce'):
        self.user_agents = user_agents

    # 从settings构造，USER_AGENTS定义在settings.py中
    @classmethod
    def from_settings(cls, settings):
        return cls(settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        #这句话用于随机选择user-agent
        ua = random.choice(self.user_agents)
        if ua:
            request.headers.setdefault('User-Agent', ua)

    def process_response(self, request, response, spider):
        # print nunormal http status response
        if 200 != response.status:
            logger.info('Crawled (%d) <GET %s>' % (response.status,response.url))
        return response


class ProxyMiddleware(object):
    """ 使用代理IP """
    proxies = list()
    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
        else:
            self.get_proxies()
            proxy = random.choice(self.proxies)
        request.meta['proxy'] = "http://%s" % proxy
        # print request.meta['proxy']
        """ 如若使用的代理ip需要验证,再一句需求修改此处代码
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        else:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']"""
    def process_exception(self, request, exception, spider):
        proxy = request.meta['proxy']
        try:
            print "remove the old proxy: " + proxy
            self.proxies.remove(proxy)
        except ValueError:
            pass
    def get_proxies(self):
        """更新代理ip"""
        self.proxies = ['122.5.128.110:808']
        """
        加入更新代理ip的方法
        """