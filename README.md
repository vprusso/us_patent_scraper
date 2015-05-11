# US Patent Scraper
A scraper for the US patents website (http://www.uspto.gov/)

This script requires the open source Python scraping library, Scrapy:
http://scrapy.org/

## Goal:
To obtain the following list of information from a user-specified search of US patents: 
	1. Patent Number
	2. US Patent Class Number
	3. International Patent Class Number
	4. Inventor Country Code 
	5. Document Identifier
	6. Abstract
	7. Patent File Date
	8. Patent Granted Date
	9. Inventor Names
	10. Patent Name
The URLs are read from "us_patent_urls.txt" and scrapes each search result. The results of each patent are then collected into a .json file. 
