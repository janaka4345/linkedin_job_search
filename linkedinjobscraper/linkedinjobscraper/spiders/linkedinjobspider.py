import scrapy


class LinkedinjobspiderSpider(scrapy.Spider):
    name = "linkedinjobspider"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response):
        pass
