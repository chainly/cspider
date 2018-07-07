# coding: utf-8
import os
import json
import base64
import logging
import copy
import scrapy
import scrapy_splash
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from fspider.models import Crawlpage, Webpage, Keyword

log = logging.getLogger(__name__)
pwd = os.path.join(os.path.dirname(os.path.abspath(__file__)))

class TestSpider(scrapy.Spider):
    name = 'test3'
    #start_urls = ['http://www.zjzfcg.gov.cn/purchaseNotice/index.html?_=1530605759118']
    lua_source = open(os.path.join(pwd, 'pagination.lua'), encoding='utf-8').read()
    splash_meta = {
        'splash': {
            'args': {
                # set rendering arguments here
                'html': 1,
                #'png': 1,

                # 'url' is prefilled from request url
                # 'http_method' is set to 'POST' for POST requests
                # 'body' is set to request body for POST requests
                # wait for js
                'wait': 3,
            },

            # optional parameters
            'endpoint': 'render.html',  # optional; default is render.json
            # 'splash_url': '<url>',      # optional; overrides SPLASH_URL
            'slot_policy': scrapy_splash.SlotPolicy.PER_DOMAIN,
            'splash_headers': {},  # optional; a dict with headers sent to Splash
            # don't set to be True, ensure `_url` is not splash_url 
            #'dont_process_response': True,  # optional, default is False
            'dont_send_headers': True,  # optional, default is False
            'magic_response': False,  # optional, default is True
        }
    }

    def get_splash_meta(self, **kwargs):
        assert 'splash' not in kwargs, 'splash keyword not allowed!'

        meta = copy.deepcopy(self.splash_meta)
        meta.update(kwargs.items())
        return meta

    def start_requests(self):
        for item in ['http://www.zjzfcg.gov.cn/purchaseNotice/index.html?_=1530605759118']:
            yield scrapy.Request(item, meta=self.get_splash_meta(django_item=None))

    def parse(self, response):
        print(response.__class__.__name__)
        django_item = response.meta.get('django_item', None)
        coding = getattr(response, 'encoding', 'utf-8')
        #data = json.loads(response.text)
        #with open('websnap.png', 'wb') as fp:
            #fp.write(base64.b64decode(data["png"]))
        ## print( response.xpath('//a/text()').extract() , response.xpath('//a[@class="next"]'))
        ## print( response.xpath('//a[contains(./text(), "下一页)]').extract())
        for slink in response.xpath('//a'):
            #print(slink, slink.root, dir(slink.root), list(slink.root.keys()))
            """
            <Selector xpath='//a' data='<a href="#">002</a>'>
            <Element a at 0x11319fe58>
            [
            'addnext', 'addprevious', 'append', 'attrib', 'base', 'base_url', 'body', 'classes', 'clear', 'cssselect', 'drop_tag', 
            'drop_tree', 'extend', 'find', 'find_class', 'find_rel_links', 'findall', 'findtext', 'forms', 'get', 'get_element_by_id', 
            'getchildren', 'getiterator', 'getnext', 'getparent', 'getprevious', 'getroottree', 'head', 'index', 'insert', 'items', 'iter', 
            'iterancestors', 'iterchildren', 'iterdescendants', 'iterfind', 'iterlinks', 'itersiblings', 'itertext', 'keys', 'label', 
            'make_links_absolute', 'makeelement', 'nsmap', 'prefix', 'remove', 'replace', 'resolve_base_href', 'rewrite_links', 'set', 'sourceline', 
            'tag', 'tail', 'text', 'text_content', 'values', 'xpath']
            ['href', 'class']
            """
            elink = slink.root
            text = elink.get('title', '') or elink.text or ''
            href = elink.get("href", '').strip()
            print(text.encode(coding), href)
            print(text, href)

            # next page
            if text in ['>']:
                if href:
                    #print('next:', href.encode(coding), text.encode(coding))
                    ## 2018-06-28 16:10:59 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://www.ccgp.gov.cn/cggg/dfgg/index_1.htm> (referer: http://www.ccgp.gov.cn/cggg/dfgg/)
                    ## @TODO: anyway use it directly!?
                    #req = response.follow(slink, callback=self.parse, errback=self.errback, meta=self.get_splash_meta(django_item=django_item))
                    ##print(req.meta)
                    ##req.meta.pop('splash' , None)
                    #yield req
                    continue
                # pagination with js
                else:
                    meta=self.get_splash_meta(django_item=django_item)
                    meta["splash"]["args"]["lua_source"] = self.lua_source
                    meta["splash"]["args"]["next"] = text
                    meta["splash"]["endpoint"] = 'execute'
                    req = response.follow('#', callback=self.print_response, errback=self.errback, meta=meta, dont_filter=True)
                    print(req.url)
                    yield req
                    continue                    
            continue


    def errback(self, failure):
        print(failure.request.url, failure, failure.getTraceback())
        
    def print_response(self, response):
        print(response.__class__.__name__)        
        print(json.loads(response.text))
        django_item = Crawlpage.objects.get(id=1)
        for title, href in json.loads(response.text)["links"].items():
            req = response.follow(href, callback=self.content_parser, errback=self.errback, meta=self.get_splash_meta(django_item=django_item))
            #print(req.meta)
            req.meta.pop('splash' , None)
            yield req
            continue                 

    def content_parser(self, response):
        """we may use restful API"""
        coding = getattr(response, 'encoding', 'utf-8')        
        print(response.url, response.xpath('//title').extract_first(default='').encode(coding))
        new = Webpage()
        new.site = response.url.strip()
        new.title = response.xpath('//title/text()').extract_first(default='') \
            + ' ' \
            + response.xpath('//h1/text()').extract_first(default='') \
            + ' ' \
            + response.xpath('//h2/text()').extract_first(default='')
        new.crawled = response.meta.get('django_item', None)
        new.status = 1 # if any([ k in str(new.title) for k in self.crawl_keyword]) else 0
        try:
            new.save()
        except Exception as err:
            log.error('save failed', exc_info=err)
