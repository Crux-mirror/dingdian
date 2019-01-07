# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import hashlib
import redis
class DingdianPipeline(object):
    def __init__(self):
        client = MongoClient('127.0.0.1',27017)
        #连接数据库
        self.db = client.admin
        self.db.authenticate("crux","163444")
        self.db=client.dingdian
        pool = redis.ConnectionPool(host='0.0.0.0',port=6379,password='163444',db=2)
        self.r = redis.Redis(connection_pool=pool,charset='utf-8',decode_responses=True)
        if self.r.llen('_id') == 0:
            self._id = 0
        else:
            self._id = int(self.r.rpop('_id'))
            self.r.rpush('_id',self._id)
    def process_item(self, item, spider):
        #区分集合，如果flag为1，则存储到书籍集合，否则存储到各自章节集合
        if item['flag'] == 1:
            bookcase = self.db['books']
            self.save_books(item,bookcase)
        else:
            book_name = item['book_name']
            book = self.db[book_name]
            self.save_content(item,book)
        return item
    def save_books(self,item,bookcase):
        bookcase.insert({"category":item["category"],"book_name":item["book_name"],
        "book_id":item["book_id"],"book_author":item["book_author"],
        "book_url":item["book_url"],"book_status":item["book_status"],"length":item["length"],
        "latest_update_time":item["latest_update_time"],"book_img_url":item["book_img_url"],
        "clicks":item["clicks"],"recommend":item["recommend"],"summary":item["summary"]})
        return item
    def save_content(self,item,book):
        print('====================++++++'+str(self._id))
        book.insert({"book_id":item["book_id"],"section_name":item["section_name"],"section_url":item["section_url"],
            "content":item['content'],"_id":self._id+1})
        self._id = self._id+1
        url_md5 = hashlib.md5(item['section_url'].encode('utf-8')).hexdigest()
        self.r.sadd('content_url',url_md5)
        self.r.rpush('_id',self._id)
        return item


