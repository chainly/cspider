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
from scrapy_splash.response import SplashJsonResponse, SplashTextResponse

log = logging.getLogger(__name__)
pwd = os.path.join(os.path.dirname(os.path.abspath(__file__)))


class TestSpider(scrapy.Spider):
    name = 'test2'
    #start_urls = ['http://www.ccgp.gov.cn/cggg/dfgg/']

    splash_meta = {
        'splash': {
            'args': {
                # set rendering arguments here
                'html': 1,
                # 'png': 1,

                # 'url' is prefilled from request url
                # 'http_method' is set to 'POST' for POST requests
                # 'body' is set to request body for POST requests
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
    
    lua_source = open(os.path.join(pwd, 'pagination.lua'), encoding='utf-8').read()


    def __init__(self, **kwargs):
        self.nextpage_keyword = kwargs.pop('nextpage_keyword', [])
        self.crawl_keyword = kwargs.pop('crawl_keyword', [])
        super().__init__(**kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        self = super().from_crawler(crawler, *args, **kwargs)
        self.nextpage_keyword = self.get_nextpage_keyword()
        self.crawl_keyword = self.get_crawl_keyword()
        return self

    def get_splash_meta(self, **kwargs):
        assert 'splash' not in kwargs, 'splash keyword not allowed!'

        meta = copy.deepcopy(self.splash_meta)
        meta.update(kwargs.items())
        return meta
    
    def start_requests(self):
        # https://github.com/scrapy/scrapy/issues/2949
        # `SplashDeduplicateArgsMiddleware._process_request: request.meta['splash']['xx'] = yy`
        #yield scrapy.Request('http://www.ccgp.gov.cn/cggg/dfgg/', meta=self.get_splash_meta())
        #yield scrapy.Request('http://www.bjrbj.gov.cn/csibiz/home/static/catalogs/catalog_75200/75200.html', meta=self.get_splash_meta())
        #yield scrapy.Request('http://www.jxsggzy.cn/web/jyxx/002006/002006001/3.html', meta=self.get_splash_meta())
        for item in Crawlpage.objects.filter(status=0):
            yield scrapy.Request(item.site, meta=self.get_splash_meta(django_item=item))

    def get_nextpage_keyword(self):
        words = set()
        for item in Keyword.objects.filter(types=1):
            words.add(item.word)
        return list(words)

    def get_crawl_keyword(self):
        words = set()
        for item in Keyword.objects.filter(types=0):
            words.add(item.word)
        return list(words)

    def parse(self, response):
        django_item = response.meta.get('django_item', None)
        coding = getattr(response, 'encoding', 'utf-8')
        #print(response.__dict__)
        # print( response.xpath('//a/text()').extract() , response.xpath('//a[@class="next"]'))
        # print( response.xpath('//a[contains(./text(), "下一页)]').extract())
        link_items = ()
        if isinstance(response, SplashJsonResponse):
            link_items = json.loads(response.text)["links"].items()
        else:
            link_items = response.xpath('//a') 
        for slink in link_items:
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
            if isinstance(slink, tuple):
                text, href = slink
            else:
                elink = slink.root
                text = elink.get('title', '') or elink.text or ''
                href = elink.get("href", '').strip()
                print(text.encode(coding), href)

            if not href or not text:
                continue
            
            req = response.follow(href, callback=self.parse, errback=self.errback)
            
            # done for this task
            if self.if_crawled(req.url):
                # maybe some error in crawl next page, so we can try again!
                continue
            # next page
            if text in self.nextpage_keyword:
                print('next:', href.encode(coding), text.encode(coding))
                # pagination with js                
                if href in ['', ]:
                    meta=self.get_splash_meta(django_item=django_item)
                    meta["splash"]["args"]["lua_source"] = self.lua_source
                    meta["splash"]["args"]["next"] = text
                    meta["splash"]["endpoint"] = 'execute'
                    req = response.follow('#', callback=self.parse, errback=self.errback, meta=meta, dont_filter=True)
                    #print(req.url)
                    yield req
                else:
                    # 2018-06-28 16:10:59 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://www.ccgp.gov.cn/cggg/dfgg/index_1.htm> (referer: http://www.ccgp.gov.cn/cggg/dfgg/)
                    # @TODO: anyway use it directly!?
                    req = response.follow(href, callback=self.parse, errback=self.errback, meta=self.get_splash_meta(django_item=django_item))
                    #print(req.meta)
                    #req.meta.pop('splash' , None)
                    yield req
                    continue
            
            #ignore pagination id
            if text.strip().isdigit():
                continue
            # ignore some innner link
            if len(text) <= 10:
                # save it, so no log more
                new = Webpage()
                new.site = req.url
                new.crawled = django_item
                try:
                    new.save()
                except Exception:
                    pass
                continue

            print(text.encode(coding), href.encode(coding))
            """安徽阜阳市加快推进养老服务体系建设 http://www.ccgp.gov.cn/gpsr/zhxx/df/201806/t20180626_10162269.htm
            联系我们 /contact.shtml
            意见反馈 mailto:feedback@ccgp.gov.cn
            """
            # *response.request.meta is response.meta*
            req = response.follow(href, callback=self.content_parser, errback=self.errback, meta={"django_item": django_item})
            # 301/302
            req.meta["__original_url"] = req.url
            #print(req.meta)
            #import sys
            #sys.exit()
            yield req

    def if_crawled(self, url, **kwargs):
        try:
            item = Webpage.objects.get(site=url.strip())
        except Webpage.DoesNotExist as err:
            # ? m.models.DoesNotExist: Webpage matching query does not exist.
            log.info('%s not in Webpage: for %r, analyse it!' % (url, kwargs), exc_info=err)
            return False
        except Exception as err:
            log.error('Webpage query Exception occurred', exc_info=err)
            return True
        else:
            return True

    def errback(self, failure):
        print(failure.request.url, failure, failure.getTraceback())

    def content_parser(self, response):
        """we may use restful API"""
        original_url = response.meta.get("__original_url", '')
        coding = getattr(response, 'encoding', 'utf-8')        
        print(response.url, response.xpath('//title').extract_first(default='').encode(coding))
        new = Webpage()
        new.site = original_url or response.url.strip()
        new.title = response.xpath('//title/text()').extract_first(default='') \
            + ' ' \
            + response.xpath('//h1/text()').extract_first(default='') \
            + ' ' \
            + response.xpath('//h2/text()').extract_first(default='')
        new.crawled = response.meta.get('django_item', None)
        new.status = 1 if any([ k in str(new.title) for k in self.crawl_keyword]) else 0
        try:
            new.save()
        except Exception as err:
            log.error('save failed', exc_info=err)


class MySpider(CrawlSpider):
    name = 'test1'
    #allowed_domains = ['example.com']
    start_urls = ['http://www.ccgp.gov.cn/cggg/dfgg/']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        #Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        #Rule(LinkExtractor(allow=('item\.php', )), callback='parse_item'),

        Rule(LinkExtractor(restrict_xpaths=('//a[@class="next"]',), ), callback='next',),
        #Rule(LinkExtractor(restrict_xpaths=('//li/a',), ), callback='parse_item',),

    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        print(response)
        item = scrapy.Item()
        #item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        #item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        #item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        #for c in response.xpath('//li'):
        #    item["content"] = c.text()
        #    print(item)
        #    yield item
        item["title"] = response.xpath('//title/text()')

    def next(self, response):
        print(response.xpath('//head/text()'))
