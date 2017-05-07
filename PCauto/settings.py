# -*- coding: utf-8 -*-

# Scrapy settings for PCauto project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'PCauto'

SPIDER_MODULES = ['PCauto.spiders']
NEWSPIDER_MODULE = 'PCauto.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'PCauto (+http://www.yourdomain.com)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'PCauto.middlewares.PcautoSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'PCauto.middlewares.MyCustomDownloaderMiddleware': 543,
#}
DOWNLOADER_MIDDLEWARES = {
     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
     'PCauto.middlewares.RotateUserAgentMiddleware' :543
}
# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'PCauto.pipelines.BrandInfoPipeline': 300,
   'PCauto.pipelines.BrandConfigPipeline': 301,
   'PCauto.pipelines.BrandBaojiaPipeline': 302,
   'PCauto.pipelines.UsedCarPipeline': 303,
   'PCauto.pipelines.ArticlePipeline': 304,
   'PCauto.pipelines.PicUrlPipeline': 305,
   'PCauto.pipelines.YouhuiPipeline': 306,
   'PCauto.pipelines.CommentPipeline': 307,
   'PCauto.pipelines.OwnerPricePipeline': 308,
   'PCauto.pipelines.BaoyangPipeline': 309,
   'PCauto.pipelines.ForumPipeline': 310,
   'PCauto.pipelines.DealerContactPipeline': 311,
   'PCauto.pipelines.DealerModelPipeline': 312,
   'PCauto.pipelines.DealerMarketPipeline': 313,
   'PCauto.pipelines.DealerNewsPipeline': 314,
   'PCauto.pipelines.MallGCTPipeline': 315,
   'PCauto.pipelines.MallImportPipeline': 316,
   'PCauto.pipelines.ChedaiPipeline': 317,
   'PCauto.pipelines.DealerPipeline': 318,
   'PCauto.pipelines.VideoPipeline': 319,
   'PCauto.pipelines.HangqingPipeline': 320,
   'PCauto.pipelines.NewCarPipeline': 321,
   'PCauto.pipelines.DaogouPipeline': 322,
   'PCauto.pipelines.PingcePipeline': 323,
   'PCauto.pipelines.TechPipeline': 324,
   'PCauto.pipelines.VideoBrandPipeline': 325,
   'PCauto.pipelines.YanghuPipeline': 326,
   'PCauto.pipelines.TirePipeline': 327,
   'PCauto.pipelines.MachineOilPipeline': 328,
   'PCauto.pipelines.GaizhuangPipeline': 329,
   'PCauto.pipelines.HangyePipeline': 330,
   'PCauto.pipelines.MotoSportPipeline': 331,
   'PCauto.pipelines.CulturePipeline': 332,
   'PCauto.pipelines.KejiPipeline': 333,
   'PCauto.pipelines.HangjiaPipeline': 334,
   'PCauto.pipelines.BaikePipeline': 335,
   'PCauto.pipelines.ProductPipeline': 336,
   'PCauto.pipelines.ChepinPipeline': 337,
   'PCauto.pipelines.RankPipeline': 338,
}

USER_AGENTS = [
   "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
   "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
   "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
   "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
   "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
   "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
   "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
   "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

LOG_STDOUT=True
# LOG_FILE = './log.txt'
# LOG_LEVEL = 'INFO'

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True


MONGODB_SERVER = "192.168.197.132"
MONGODB_PORT = 27017
MONGODB_DB = "PCauto"

REDIS_HOST = "192.168.197.132"
REDIS_PORT = 6379
