# -*- coding: utf-8 -*-
import scrapy


class NovelSpider(scrapy.Spider):
    name = 'novel'
    allowed_domains = ['23us.so']
    start_urls = ['http://23us.so/']

    def parse(self, response):
        pass
