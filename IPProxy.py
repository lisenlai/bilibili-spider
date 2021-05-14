#从ip池中获取ip，用来改变requests.get方法的proxies
import random
import requests
import hashlib
import time
import datetime

class IPProxy():
    proxys = []
    last_updateproxys_time = 0

    @classmethod
    def getIp(cls):
        return cls.get_random_proxy()

    @classmethod
    def get_random_proxy(cls):
        #根据ip池获取随机ip
        now = time.time()
        if (now - cls.last_updateproxys_time > 150):
            cls.update_proxys()
            cls.last_updateproxys_time = now
        return {"https:": "https://" + random.choice(cls.proxys)}

    @classmethod
    def update_proxys(cls):
        #购买的是engeniusiot.com的ip套餐，根据获取的ip构建ip池，每两分半钟更新一次，请根据自己的套餐修改相关参数
        cls.proxys = []
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        order_id = "49046"
        username = "清水雕饰"
        password = str(hashlib.md5("qwer4371273".encode(encoding="UTF-8")).hexdigest())
        timestamp = str(now)
        md = str(hashlib.md5((username+order_id+password+timestamp).encode(encoding='UTF-8')).hexdigest())
        num = 10
        format1 = "text"
        url = "https://apis.engeniusiot.com/api/getips?order_id=%s&username=%s&md5=%s&timestamp=%s&num=%d&format=%s"%(order_id,
        username,md,timestamp,num,format1)
        response = requests.get(url)
        cls.proxys = response.text.split("\n")[:-1]    