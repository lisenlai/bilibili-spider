# item处理管道，将书籍item和评论item里的值存到mysql数据库
from urllib.parse import parse_qs
from itemadapter import ItemAdapter
import pymysql
from bilibiliSpider.items import UserItem
from bilibiliSpider.items import VideoItem
from bilibiliSpider.items import FollowFansItem
import redis
from pymysql.converters import escape_string

class MysqlPipeline():
    conn = None
    cursor = None
    def open_spider(self, spider):
        #打开管道，连接到mysql数据库，如果没有user,video和followfans数据表，就创建
        user = "root"
        password = ""
        database = "bilibili"
        port = 3306
        self.conn = pymysql.Connect(host='127.0.0.1', port = port, user = user, password = password, db=database,charset='utf8')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""create table if not exists `user`(
                uid int primary key,
                uname char(50),
                follow_num int,
                fans_num int)
                """)
            self.cursor.execute("""create table if not exists `video`(
                vid char(50),
                title char(255),
                type char(10),
                uid int,
                favlist_name char(255))
                """)
            self.cursor.execute("""create table if not exists `followfans`(
                follow int,
                fans int)
                """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()


    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            sql = """
                    replace into `user` (uid, uname, follow_num, fans_num)
                    values(%s, %s, %s, %s)
                  """
            self.cursor.execute(sql, (item['uid'], item['uname'], item['follow_num'], item['fans_num']))
        elif isinstance(item, VideoItem):
            sql = """
                    insert into `video` (vid, title, type, uid, favlist_name)
                    values(%s, %s, %s, %s, %s)
                  """
            self.cursor.execute(sql, (item['vid'], item['title'], item['type'], item['uid'], item['favlist_name']))
        elif (isinstance(item, FollowFansItem)):
            sql = """
                    insert into `followfans` (follow, fans)
                    values(%s, %s)
                  """
            self.cursor.execute(sql, (item['follow'], item['fans']))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        #关闭数据库的连接
        self.cursor.close()
        self.conn.close()