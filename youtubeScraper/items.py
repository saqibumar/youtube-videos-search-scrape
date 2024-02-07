# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
import scrapy

""" class ScraperItem(scrapy.Item):
	page = scrapy.Field()
	content = scrapy.Field()


class PageContentItem(Item):
    url = Field()
    content = Field()
    pass """

class ScraperItem(Item):
    page = Field()
    content = Field()
    links = Field()
    image = Field()
    video = Field()
    image_urls=Field()
    images=Field()
    base64images=Field()
    video=Field()
    lat = Field()
    lon = Field()
    country = Field()
    NoozId = Field()
    REQ_ID = Field()
    DisplayPosition = Field()
    VideoImageFile = Field()
