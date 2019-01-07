# -*- coding: utf-8 -*-
import scrapy
import copy
from scrapy import log
import re
import time
from dingdian.items import DingdianItem,ContentItem
import redis
import hashlib
class NovelSpider(scrapy.Spider):
    name = 'page'
    allowed_domains = ['23us.so']
    n = 1
    start_urls = ['https://www.23us.so/xiaoshuo/'+str(n)+'.html',
                    'https://www.23us.so/xiaoshuo/2.html']

    pool = redis.ConnectionPool(host='0.0.0.0',port=6379,password='163444',db=2)
    r = redis.Redis(connection_pool=pool,charset='utf-8',decode_responses=True)

    def start_requests(self):
         while self.n < 400:
             yield scrapy.Request(url='https://www.23us.so/xiaoshuo/'+str(self.n)+'.html',callback=self.parse_books)
             self.n+=1
    #def start_requests(self):
    #    for url in self.start_urls:
    #        yield scrapy.Request(url,callback=self.parse_books)
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
        url_md5 = hashlib.md5(item['book_url'].encode('gb2312')).hexdigest()
        if self.r.sadd('books',url_md5):
            yield item
        yield scrapy.Request(url=catalog,callback=self.parse_catalog)

    def parse_catalog(self, response):
        #解析目录章节
        #lists = response.xpath('//tr/td/a/text()').extract()
        #first_url = response.xpath('//*[@id="at"]/tr[1]/td[1]/a/@href').extract_first()
        #urls = response.xpath('//tr/td/a/@href').extract()
        lists = response.xpath('//*[@id="at"]/tr/td/a/@href').extract()
        for first_url in lists:
            url_md5 = hashlib.md5(first_url.encode('utf-8')).hexdigest()
            print(url_md5+'*****************************************')
            if not self.r.sismember('content_url',url_md5):
                yield scrapy.Request(url=first_url,callback=self.parse,priority=14,meta={'download_timeout':5})
                break
            else:
                continue

    def parse(self, response):
        #解析章节内容，并交由pipeline保存
        url = response.url
        print(url+'-----------------------------------------')
        item = ContentItem()
        item['section_name'] = response.xpath('//*[@id="amain"]/dl/dd[1]/h1/text()').extract_first().strip()
        item['section_url'] = url
        item['content'] = response.xpath("//div[@id='amain']/dl/dd[@id='contents']/text()").extract()
        #item['content'] = response.css("#contents").extract()[0].replace('<br>','').strip()
        item['book_name'] = response.xpath('//*[@id="amain"]/dl/dt/a[3]/text()').extract_first()
        item['book_id'] = re.findall('[0-9]+',url)[2]
        item['flag'] = 2
        next_url = response.xpath('//*[@id="footlink"]/a[3]/@href').extract_first()
        yield item
        if re.findall('.*/(.*?)\.html',next_url)[0] == 'index':
            return None
        next_url = 'https://www.23us.so'+next_url
        #item['no']
        yield scrapy.Request(url=next_url,callback=self.parse,priority=15,meta={'download_timeout':5})

