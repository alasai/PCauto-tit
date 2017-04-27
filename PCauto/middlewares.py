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

