# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DingdianItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    book_name = scrapy.Field()
    book_id = scrapy.Field()
    book_author = scrapy.Field()
    book_url = scrapy.Field()
    book_status = scrapy.Field()
    latest_update_time = scrapy.Field()
    book_img_url = scrapy.Field()
    clicks = scrapy.Field()
    recommend = scrapy.Field()
    flag = scrapy.Field()
    summary = scrapy.Field()
    category = scrapy.Field()
    length = scrapy.Field()
    #小说图片下载到固定的django？还是直接用网络图片 暂定网络图片
class ContentItem(scrapy.Item):
    book_id = scrapy.Field()
    book_name = scrapy.Field()
    section_name = scrapy.Field()
    section_url = scrapy.Field()
    flag = scrapy.Field()
    content = scrapy.Field()

