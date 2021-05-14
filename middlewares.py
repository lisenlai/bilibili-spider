# scray的中间件，在这里使用selenium谷歌无头浏览器发起请求，并在请求中修改UA及ip

from scrapy import signals
from itemadapter import is_item, ItemAdapter
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http.response.html import HtmlResponse
import random
import requests
import hashlib

class seleniumDownloadMiddleware:
    #selenium下载中间件

    proxys = []
    last_updateproxys_time = 0
    #UA池
    user_agent = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTMkL, lie Gecko) Version/4.0 Mobile Safari/533.1",
        "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
        "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13"
    ]
    def __init__(self):
        #使用谷歌无头浏览器
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("lang=zh-CN.UTF-8")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def get_random_proxy(self):
        #根据ip池获取随机ip
        now = time.time()
        if (now - self.last_updateproxys_time > 150):
            self.update_proxys()
            self.last_updateproxys_time = now
        return random.choice(self.proxys)

    def update_proxys(self):
        #购买的是engeniusiot.com的ip套餐，根据获取的ip构建ip池，每两分半钟更新一次，请根据自己的套餐修改相关参数
        self.proxys = []
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        order_id = ""
        username = "清水雕饰"
        password = str(hashlib.md5("".encode(encoding="UTF-8")).hexdigest())
        timestamp = str(now)
        md = str(hashlib.md5((username+order_id+password+timestamp).encode(encoding='UTF-8')).hexdigest())
        num = 20
        format1 = "text"
        url = "https://apis.engeniusiot.com/api/getips?order_id=%s&username=%s&md5=%s&timestamp=%s&num=%d&format=%s"%(order_id,
        username,md,timestamp,num,format1)
        response = requests.get(url)
        self.proxys = response.text.split("\n")[:-1]      

    def process_request(self, request, spider):
        #仅在网址属于哔哩哔哩网站时修改proxy
        request.headers['User-Agent'] = random.choice(self.user_agent)
        if ("bilibili.com" in request.url):
            request.meta['proxy'] = self.get_random_proxy()
        self.driver.get(request.url)
        response = HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)
        return response

    def process_exception(self, request, exception, spider):
        print(exception)