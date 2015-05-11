'''
main.py: *(Note this script requires Scrapy to be installed)
    Reads the URLs from "us_patent_urls.txt" and scrapes each search result. 
    The results of each patent are then collected into a .json file. 
'''

import os

output_file_name = "items"
os.system("scrapy crawl uspat -o "+ output_file_name +".json")

