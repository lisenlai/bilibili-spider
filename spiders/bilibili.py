# 爬取bilibili网站用户的个人信息、粉丝数、关注数以及上传和收藏夹视频信息。
from scrapy.http import request
from bilibiliSpider.items import UserItem
import scrapy
from scrapy.http import Request
from bilibiliSpider.items import VideoItem
from bilibiliSpider.items import FollowFansItem
from bilibiliSpider.IPProxy  import IPProxy
import time
import json
import requests
class BilibiliSpider(scrapy.Spider):
    name = 'bilibili'
    start_urls = ['https://bilibili.com']
    uid = 1
    f_params = {
        "vmid": str(uid),
        "pn": "1",
        "ps": "50",
        "order": "desc",
        "jsonp": "jsonp",
        "callback": "__jp3"
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Referer': 'https://space.bilibili.com/'+str(uid)+'/fans/follow',

    }
    f_url = "https://api.bilibili.com/x/relation/"

    def parse(self, response):
        spider_type = input("请选择：1爬取指定uid的用户，2爬取uid为1——5000的用户\n")
        yield from self.choose(spider_type = spider_type)

    def choose(self, spider_type):
        if spider_type == "1":
            #爬取指定uid的用户
            x = input("输入纯数字uid，输入其他字符结束爬虫： ")
            while x.isdigit():
                self.uid = x
                yield from self.parse_user()
                x = input("输入纯数字uid，输入其他字符结束爬虫： ")
        else:
            #爬取uid为1-5000的用户
            for i in range(1, 5000):
                self.uid = i
                yield from self.parse_user()
    
    def parse_user(self):
        # 解析用户信息
        userItem = UserItem()
        userItem['uid'] = self.uid
        self.headers["Referer"] = "https://space.bilibili.com/" + str(self.uid)
        params = {"mid": str(self.uid), "jsonp": "jsonp"}
        r = requests.get("https://api.bilibili.com/x/space/acc/info", params = params, headers = self.headers, proxies=IPProxy.getIp()) 
        if ("data" not in json.loads(r.text)):
            return
        userItem["uname"] = json.loads(r.text)["data"]["name"]
        params = {"vmid": str(self.uid), "jsonp": "jsonp1"}
        r = requests.get("https://api.bilibili.com/x/relation/stat", params = params, headers = self.headers, proxies=IPProxy.getIp())
        if ("data" not in json.loads(r.text)):
            return
        userItem["follow_num"] = json.loads(r.text)["data"]["following"]
        userItem["fans_num"] = json.loads(r.text)["data"]["follower"]
        yield userItem

        yield from self.parse_fans({"type": "follow", "index": "1"})    
        if (userItem["follow_num"] > 50):
                yield from self.parse_fans({"type": "follow", "index": "2"})
            

        yield from self.parse_fans({"type": "fans", "index": "1"})    
        if (userItem["fans_num"] > 50):
                yield from self.parse_fans({"type": "fans", "index": "2"})
        
        yield from self.parse_favlist()
        
        yield from self.parse_uploadlist()
        

    def parse_fans(self, kwargs):
        #解析粉丝以及关注人的信息
        self.f_params["vmid"] = str(self.uid)
        f_url = ""
        if (kwargs['type'] == "follow"):
            self.headers['Referer'] = 'https://space.bilibili.com/'+str(self.uid)+'/fans/follow'
            f_url = self.f_url + "followings"
        else:
            self.headers['Referer'] = 'https://space.bilibili.com/'+str(self.uid)+'/fans/fans'
            f_url = self.f_url + "followers"
        if (kwargs['index'] == "1"):
            self.f_params['pn'] = "1"
        else:
            self.f_params['pn'] = '2'
    
        r = requests.get(f_url, headers = self.headers, params = self.f_params, proxies=IPProxy.getIp())
        if ('data' not in json.loads(r.text[6:-1])):
            return 
        follow_list = json.loads(r.text[6:-1])['data']['list']
        for i in follow_list:
            item = FollowFansItem()
            if (kwargs["type"] == "follow"):
                item["fans"] = self.uid
                item["follow"] = i["mid"]
            else:
                item["follow"] = self.uid
                item["fans"] = i["mid"]
            yield item

    def parse_favlist(self):
        # 收藏夹的视频
        all_list_url = "https://api.bilibili.com/x/v3/fav/folder/created/list-all"
        self.headers['Referer'] = "https://space.bilibili.com/"+str(self.uid)+"/favlist"
        params = {
            "up_mid": str(self.uid),
            "jsonp": "jsonp"
        }
        r = requests.get(all_list_url, headers=self.headers,params=params, proxies=IPProxy.getIp())
        all_list = json.loads(r.text)
        if (all_list['data'] is None):
            return
        flist_url = "https://api.bilibili.com/x/v3/fav/resource/list"
        for flist in all_list['data']['list']:
            params = {
                "media_id": flist["id"],
                "ps": "20",
                "keyword": "",
                "order": "mtime",
                "type": "0",
                "tid": "0",
                "platform": "web",
                "jsonp": "jsonp"
            }
            v_count = 0
            v_index = 1
            while(v_count < flist["media_count"]):
                params["pn"] = v_index
                r2 = requests.get(flist_url, headers=self.headers, params = params, proxies=IPProxy.getIp())
                for i in json.loads(r2.text)['data']['medias']:
                    yield from self.fav_video_item(i = i, favlist_name = flist['title'])
                v_index = v_index + 1
                v_count = v_count + 20
                

    def parse_uploadlist(self):
        # 上传的视频
        url = "https://api.bilibili.com/x/space/arc/search"
        self.headers["Referer"] = "https://space.bilibili.com/"+str(self.uid)
        params = {
            "mid": self.uid,
            "ps": "50",
            "tid": "0",
            "pn": "1",
            "keyword": "",
            "order": "pubdate",
            "jsonp": "jsonp"
        }
        r = requests.get(url, headers= self.headers, params = params, proxies=IPProxy.getIp())
        data_dict = json.loads(r.text)
        if (data_dict['data']['page']['count'] is None):
            return
        video_count = int(data_dict['data']['page']['count'])
        for i in data_dict['data']['list']['vlist']:
            yield from self.up_video_item(i)
        sum = 50
        index = 1
        while (sum < video_count):
            sum = sum + 50
            index = index + 1
            params["pn"] = index
            r = requests.get(url, headers= self.headers, params = params, proxies=IPProxy.getIp())
            data_dict = json.loads(r.text)    
            for i in data_dict['data']['list']['vlist']:
                yield from self.up_video_item(i)
    
    def up_video_item(self, i):
        vitem = VideoItem()
        vitem['vid'] = i["bvid"]
        vitem['title'] = i["title"]
        vitem['type'] = "upload"
        vitem["uid"] = self.uid
        vitem["favlist_name"] = None
        yield vitem
    
    def fav_video_item(self, i, favlist_name):
        vitem = VideoItem()
        vitem['vid'] = i["bvid"]
        vitem['title'] = i["title"]
        vitem['type'] = "favorite"
        vitem['favlist_name'] = favlist_name
        vitem["uid"] = self.uid
        yield vitem