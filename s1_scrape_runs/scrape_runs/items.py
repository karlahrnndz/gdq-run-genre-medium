# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class RunItem(scrapy.Item):
    name = scrapy.Field()  # Scraped from event bids table
    runners = scrapy.Field()  # Scraped from event bids table
    hosts = scrapy.Field()  # Scraped event from bids table
    commentators = scrapy.Field()  # Scraped from event bids table
    description = scrapy.Field()  # Scraped from event bids table
    start_time = scrapy.Field()  # Scraped from event bids table
    run_time = scrapy.Field()  # Scraped from event bids table
    bid_wars = scrapy.Field()  # Scraped from event bids table
    event = scrapy.Field()  # Additional desired field
    run_id = scrapy.Field()  # Additional desired field