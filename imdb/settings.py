BOT_NAME = "imdb"
SPIDER_MODULES = ["imdb.spiders"]
NEWSPIDER_MODULE = "imdb.spiders"

DOWNLOAD_HANDLERS = {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    }

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "timeout" : 120000
}

ADDONS = {}

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 5

COOKIES_ENABLED = True

DOWNLOADER_MIDDLEWARES = {
    'imdb.middlewares.RandomHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

ITEM_PIPELINES = {
    'imdb.pipelines.ImdbPipeline': 300,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1

RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
LOG_LEVEL = "INFO"
FEED_EXPORT_ENCODING = "utf-8"
