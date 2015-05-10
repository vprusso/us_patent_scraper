# -*- coding: utf-8 -*-
"""Item fields for the Scrapy patent crawler"""

from scrapy.item import Field

import scrapy


class PatentSpiderItem(scrapy.Item):
    
    # Basic information
    patent_name = scrapy.Field()
    patent_num = scrapy.Field()
    abstract = scrapy.Field()

    # Inventors / etc.    
    assignee = scrapy.Field()
    family_id = scrapy.Field()
    appl_no = scrapy.Field()    
    filed_date = scrapy.Field()
    granted_date = scrapy.Field()

    inventor_first_name = scrapy.Field()
    inventor_last_name = scrapy.Field()
    inventor_country_code = scrapy.Field()

    pct_filed_date = scrapy.Field()
    pct_num = scrapy.Field()
    pct_pub_num = scrapy.Field()
    pct_pub_date = scrapy.Field()
    
    # Prior publication date
    document_identifier = scrapy.Field()
    publication_date = scrapy.Field()    
    
    session_id = scrapy.Field()
    current_url = scrapy.Field()
    referring_url = scrapy.Field()

    # Other misc. info
    us_classes = scrapy.Field()
    international_classes = scrapy.Field()