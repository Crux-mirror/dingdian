# -*- coding: utf-8 -*-
import scrapy
import copy
from scrapy import log
import re
import time
from dingdian.items import DingdianItem,ContentItem

class NovelSpider(scrapy.Spider):
    name = 'dingdian'
    allowed_domains = ['23us.so']
    n = 1
    start_urls = ['https://www.23us.so/xiaoshuo/'+str(n)+'.html']
    # def start_requests(self):
    #     while self.n < 400:
    #         yield scrapy.Request(url='https://www.23us.so/xiaoshuo/'+str(self.n)+'.html',callback=self.parse_books)
    #         n+=1
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,callback=self.parse_books)
    def parse_books(self,response):
        #解析书籍概述等首页
        item = DingdianItem()
        item['category'] = response.xpath('//tr/td[1]/a/text()').extract_first() #小说类别
        item['book_author'] = response.xpath('//tr[1]/td[2]/text()').extract_first().strip() #小说作者去掉前后空格
        item['book_id'] = re.findall(r'/[0-9]+',response.url)[0][1:]
        item['book_name'] = response.xpath('//*[@id="content"]/dd[1]/h1/text()').extract_first()[:-4] #小说名字
        item['book_status'] = response.xpath('//tr[1]/td[3]/text()').extract_first().strip() #小说状态
        item['book_url'] = response.url
        item['clicks'] = response.xpath('//tr[3]/td[1]/text()').extract_first().strip() #总点击数
        item['recommend'] = response.xpath('//tr[4]/td[1]/text()').extract_first().strip() #总推荐数
        item['book_img_url'] = response.xpath('//*[@id="content"]/dd[2]/div[1]/a/img/@src').extract_first()
        item['summary'] = response.xpath('//dd/p[2]').extract_first() #简介
        item['length'] = response.xpath('//tr[2]/td[2]/text()').extract_first().strip() #总字数
        item['latest_update_time'] = response.xpath('//tr[2]/td[3]/text()').extract_first().strip() #最后更新时间
        item['flag'] = 1 
        catalog = response.xpath('//div/p[2]/a[1]/@href').extract_first()  #书籍目录
        yield item
        yield scrapy.Request(url=catalog,callback=self.parse_catalog)

    def parse_catalog(self, response):
        #解析目录章节
        #lists = response.xpath('//tr/td/a/text()').extract()
        urls = response.xpath('//tr/td/a/@href').extract()
        for content_url in urls:
            print(content_url+'=====================================')
            yield scrapy.Request(url=content_url,callback=self.parse,priority=15)

    def parse(self, response):
        #解析章节内容，并交由pipeline保存
        url = response.url
        print(url+'-----------------------------------------')
        item = ContentItem()
        item['section_name'] = response.xpath('//*[@id="amain"]/dl/dd[1]/h1/text()').extract_first().strip()
        item['section_url'] = url
        item['content'] = response.xpath("//div[@id='amain']/dl/dd[@id='contents']/text()").extract()
        item['book_name'] = response.xpath('//*[@id="amain"]/dl/dt/a[3]/text()').extract_first()
        item['book_id'] = re.findall('[0-9]+',url)[2]
        #item['no']
        item['flag'] = 2
        return item
