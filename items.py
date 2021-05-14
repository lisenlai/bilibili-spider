import scrapy

class UserItem(scrapy.Item):
    uid = scrapy.Field()     #每个b站用户独有的标识
    uname = scrapy.Field()   #用户名
    follow_num = scrapy.Field() #关注数
    fans_num = scrapy.Field()   #粉丝数

class VideoItem(scrapy.Item):
    vid = scrapy.Field()    #视频的bv号，每个B站视频的bv号都是唯一的
    title = scrapy.Field()
    type = scrapy.Field()   #favorite或者upload，收藏夹或者自己上传视频
    uid = scrapy.Field()    #属于哪位用户的收藏或者上传
    favlist_name = scrapy.Field() #如果属于收藏夹，所属收藏夹名称
    #从list开头的选项以及search开头的找
    
class FollowFansItem(scrapy.Item):
    follow = scrapy.Field() #属于关注与被关注关系中的被关注者
    fans = scrapy.Field()   #属于关注与被关注关系中的关注者