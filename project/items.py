# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ResearcherItem(scrapy.Item):

    personal_info = scrapy.Field()
    research_area_info = scrapy.Field()
    academic_studies = scrapy.Field()
    additional_training = scrapy.Field()
    jobs = scrapy.Field()
    languages = scrapy.Field()
    research_lines = scrapy.Field()
    awards = scrapy.Field()
    cientific_events = scrapy.Field()
    cientific_papers = scrapy.Field()
    books = scrapy.Field()
    software = scrapy.Field()
    academic_projects = scrapy.Field()

