BOT_NAME = 'bilibiliSpider'

SPIDER_MODULES = ['bilibiliSpider.spiders']
NEWSPIDER_MODULE = 'bilibiliSpider.spiders'
LOG_LEVEL = "ERROR"

ROBOTSTXT_OBEY = False

DOWNLOADER_MIDDLEWARES = {
    'bilibiliSpider.middlewares.seleniumDownloadMiddleware': 543,
}

ITEM_PIPELINES = {
    'bilibiliSpider.pipelines.MysqlPipeline': 300,
}