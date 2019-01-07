# _*_ coding:utf-8 _*_
import scrapy
import redis
import time
import telnetlib
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
class ProxyMiddleware(object):
    '''
    设置Ipproxy
    '''
    def __init__(self):
        self.pool = redis.ConnectionPool(host='0.0.0.0',port=6379,password='163444',db=1)
        self.r = redis.Redis(connection_pool=self.pool,charset='utf-8',decode_responses=True)
 
    def process_request(self, request, spider):
        ipport = str(self.r.srandmember('proxy'),encoding='utf-8')
        try:
            ip,port = ipport.split(':')
            telnetlib.Telnet(ip,port=port,timeout=2)
            if request.url.startswith("http://"):
                ipport = 'http://'+ipport
            elif request.url.startswith("https://"):
                ipport = 'https://'+ipport
            print(ipport)
            request.meta['proxy'] = ipport
        except:
            self.r.srem('proxy',ipport)
            print('it s failed '+ipport)
            time.sleep(2)
            self.process_request(request,spider)
        else:
            print('it s seccuss! '+ipport)
    def process_response(self,request,response,spider):
        print(str(response.status)+'===================================')
        return response
    

