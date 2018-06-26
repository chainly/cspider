import copy
import scrapy
import scrapy_splash
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class TestSpider(scrapy.Spider):
    name = 'test2'
    #start_urls = ['http://www.ccgp.gov.cn/cggg/dfgg/']
    
    def start_requests(self):
        meta = {
            'splash': {
                'args': {
                    # set rendering arguments here
                    'html': 1,
                    # 'png': 1,

                    # 'url' is prefilled from request url
                    # 'http_method' is set to 'POST' for POST requests
                    # 'body' is set to request body for POST requests
                    'dont_process_response': True
                },

                # optional parameters
                'endpoint': 'render.html',  # optional; default is render.json
                # 'splash_url': '<url>',      # optional; overrides SPLASH_URL
                'slot_policy': scrapy_splash.SlotPolicy.PER_DOMAIN,
                'splash_headers': {},  # optional; a dict with headers sent to Splash
                'dont_process_response': True,  # optional, default is False
                'dont_send_headers': True,  # optional, default is False
                'magic_response': False,  # optional, default is True
            }
        }
        # https://github.com/scrapy/scrapy/issues/2949
        # `SplashDeduplicateArgsMiddleware._process_request: request.meta['splash']['xx'] = yy`
        meta_deepcopy = copy.deepcopy(meta)
        yield scrapy.Request('http://www.ccgp.gov.cn/cggg/dfgg/', meta=meta_deepcopy)
        meta_deepcopy = copy.deepcopy(meta)
        yield scrapy.Request('http://www.bjrbj.gov.cn/csibiz/home/static/catalogs/catalog_75200/75200.html', meta=meta_deepcopy)

    def parse(self, response):
        print(list(response.__dict__.keys()))
        print( response.xpath('//a/text()').extract() , response.xpath('//a[@class="next"]'))
        print( response.xpath('//a[contains(./text(), "下一页")]').extract())
    

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
