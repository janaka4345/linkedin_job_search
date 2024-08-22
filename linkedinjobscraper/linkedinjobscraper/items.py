# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinjobscraperItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    job_url = scrapy.Field()
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    location = scrapy.Field()
