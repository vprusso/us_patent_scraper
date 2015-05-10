# -*- coding: utf-8 -*-
"""US Patent Crawler """

import re

import urllib2
from bs4 import BeautifulSoup

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector

from patent_spider.items import PatentSpiderItem

class USPatent(CrawlSpider):
    name = 'uspat'
    session_id = -1
    response_url = ""
    
    # all search terms for us patent search are saved in .txt file.
    #f = open("us_patent_urls.txt")
    f = open("us_patent_urls.txt")
    start_urls = [url.strip() for url in f.readlines()]
    f.close()
    
    rules = (
        Rule (
            SgmlLinkExtractor(
                allow=("http://patft.uspto.gov/netacgi/.*", ),),
            callback="parse_items",
            process_links="filter_links",
            follow= True),
    )


    def __init__(self, session_id=-1, *args, **kwargs):
        super(USPatent, self).__init__(*args, **kwargs)
        self.session_id = session_id


    def parse_start_url(self, response):
        self.response_url = response.url
        return self.parse_items(response)


    def parse_items(self, response):

        # Grab the URL and parse each patent link
        self.response_url = response.url
        sel = Selector(response)
        items = []
        item = PatentSpiderItem()

        # Global constants            
        MAX_INVENTOR = 7            #Maximum number of inventors
        
        nullstring = '-----'        #setting a dummy string for filler
        ccnullstring = '--'        
        
        month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', \
                       'SEP', 'OCT', 'NOV', 'DEC', \
                       'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', \
                       'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', \
                       'DECEMBER']
                   
        tabletags_list = []         #initializing lists
        fonttags_list = []
        titletags_list = []
        trtags_list = []
              
        webpage = urllib2.urlopen(response.url)
        
        #Beautiful soup outputs data as lists
        #These lists must be converted to strings using the "".join(list) function
        soup = BeautifulSoup(webpage)
        soup_content = soup.prettify()
        tabletags_list = soup.findAll("table")
        fonttags_list = soup.findAll("font")
        titletags_list = soup.findAll("title")
        trtags_list = soup.findAll("tr")
            
        # If you've encountered and followed a patent, then process each
        # piece of relevant information to store in the database.
        if sel.xpath('/html/body/font/text()').extract():

            ## GRANTED DATE:
            btagsintable2_list  = tabletags_list[2].findAll('b')
            length =  btagsintable2_list.__len__()       
            date_string = "".join(btagsintable2_list[length-1])
            granted_date = (date_string.replace('\n','')).lstrip()

            ## FILING DATE:
            filed_date_expression = re.compile('Filed:\n\s+</th>\n\s+<td align="left" width="90%">\n\s+<b>\s+(.*?)</b>',re.DOTALL)
            filed_date = re.findall(filed_date_expression,soup_content)
            filed_date_string = str(filed_date[0])
            if filed_date_string == '</b>':
                    filed_date_string = nullstring
            tmp_filed_date_str = filed_date_string.replace('     ','')
            filed_date_str = tmp_filed_date_str.replace('\n','')

            ## US CLASSES -- could be in 4th,5th, 6th or sometimes 7th table                   
            clss_tbl=4
            # Find out if we have the right table index
            if (tabletags_list[clss_tbl].findAll(text="Current U.S. Class:") == []):
                clss_tbl=5
            if (tabletags_list[clss_tbl].findAll(text="Current U.S. Class:") == []):
                clss_tbl=6     
            if (tabletags_list[clss_tbl].findAll(text="Current U.S. Class:") == []):
                clss_tbl=7    
                
            usclass_str = "".join( tabletags_list[clss_tbl].extract().findAll('td')[1].findAll(text=True) )
            us_classes = self.ClassList( usclass_str )
                                                
            ## INTERNATIONAL CLASSES -- in same table as US class
            intclass_str = "".join( tabletags_list[clss_tbl].extract().findAll('td')[3].findAll(text=True) )
            intclass_str = intclass_str.replace("&nbsp;", " ")
            intclass_str = intclass_str.replace("20060101",'')
            intclass_str = intclass_str.replace("()",'')
            intclass_str = intclass_str.replace(" ",'')
            
            international_classes = self.ClassList( intclass_str )      
            
            ############################################
            #Finding the inventors - in 3rd table
            
            inv_lastname_list = []          #initialize lists
            inv_firstname_list = []
            inv_country_list = []
           
            #the following code should be a method, because i use it again for the assignee (to do later)
            
            listlength = tabletags_list.__len__()
            i=0
            mark_position = 0
            
            while i < listlength:
                
                tabletags_string = str(tabletags_list[i]) 
                inventor_expression = re.compile('>Inventors:<',re.DOTALL)
                inventor = re.findall(inventor_expression,tabletags_string)
                
                if not inventor:                    
                    i = i + 1       #keep checking...
                else:       #found an inventor 
                    mark_position = i
                    i = listlength   #exit the while loop

                    
            if mark_position == 0:
                inventor_str = nullstring
                print "did not find inventor"
            else:   
                inventor_str = "found inventor in table tag" + str(mark_position)
                print inventor_str
            
            inventor_info   = tabletags_list[mark_position].extract()
            #print "the extracted inventor information is"
            #print inventor_info
            
            print " first grab all the b-tags --should grab at least the inventor info, usually more"
            inventor_name_expression = re.compile('<b>(.*?)</b>')
            inventor_list = re.findall(inventor_name_expression,str(inventor_info))
            listlength = inventor_list.__len__()
            print "inventor  list is"
            print inventor_list                
                
            for i in range(0, listlength):  #look for names
                fullname = "".join(inventor_list[i])
                flag = 0  #setting a flag so that a country check is done if a name is found
                #Check if the full name is there by looking for a semi-colon
           
                if fullname.find(';') >=0:
                    #flag = 1  # found a name, set this flag to do a countyr check
                    name_list = []        
                    name_list = self.ExtractName( "".join(inventor_list[i]) )
                    
                    inv_firstname_list.append("".join(name_list[0]))
                    inv_lastname_list.append("".join(name_list[1]))
                    
                #if flag == 1:
                
                if i+1 < listlength:
                        country = inventor_list[i+1]
                        if len(country) == 2:  #probably a country for the inventor
                            print "got country for inventor"
                            inv_country_list.append(country)
                        else:   
                            print "did not find country for inventor"
                            inv_country_list.append(ccnullstring)
                    
                else:
                    print ""  #do nothing               
        
        
            for i in range(listlength, MAX_INVENTOR):    #pad the rest of the inventors
                inv_firstname_list.append("")
                inv_lastname_list.append ("")        
                inv_country_list.append("")
               
            for i in range(0, inv_lastname_list.__len__()):
                    #print inv_lastname_list[i], ", ", inv_firstname_list[i], " (", inv_city_list[i], ", ", inv_country_list[i], ")"
                print inv_lastname_list[i], ", ", inv_firstname_list[i], ", ", inv_country_list[i]
                print ""
            
            ## DOCUMENT IDENTIFIER:
            # Depending on site, document identifier may be in a different table.
            doc_id = (sel.xpath('/html/body/table[4]/tr/td[2]/text()').extract()[0]).strip()
            if not (sel.xpath('/html/body/table[4]/tr/td[2]/text()').extract()):
                doc_id = (sel.xpath('/html/body/table[5]/tr[3]/td[2]/text()').extract()[0]).strip()
            
            # Check to ensure that document identifier starts with "US"
            if "US" in str(doc_id):
                item['document_identifier'] = doc_id
            
            ## PUBLICATION DATE: 
            # Depending on site, publication date may be in a different table.
            pub_id = sel.xpath('/html/body/table[4]/tr/td[3]/text()').extract()
            if not (sel.xpath('/html/body/table[4]/tr/td[2]/text()').extract()):                           
                pub_id = sel.xpath('/html/body/table[5]/tr[3]/td[3]/text()').extract()

            # Check to ensure that the publication date involves a month.
            if any(month.lower() in str(pub_id).lower() for month in month_list):            
                item['publication_date'] = pub_id
            
            
            # STORE INTO DICTIONARY:
            item['patent_name'] = (re.sub("\s\s+" , " ", str(sel.xpath('/html/body/font/text()').extract()[0]).replace("\\n",""))).strip()        
            item['patent_num'] = (sel.xpath('(/html/body/table[2]/tr/td/b/text())[2]').extract()[0]).strip()                        
            #item['abstract'] = (re.sub("\s\s+" , " ", str(sel.xpath('/html/body/p[1]/text()').extract()[0]).replace("\\n",""))).strip()
            item['abstract'] = 'dummy_abstract'
            
            item['granted_date'] = granted_date
            item['filed_date'] = filed_date
            item['us_classes'] = us_classes
            item['international_classes'] = international_classes

            item['inventor_first_name'] = inv_firstname_list            
            item['inventor_last_name'] = inv_lastname_list
            item['inventor_country_code'] = inv_country_list
            
            #item['inventors'] = inventor_list
            
            items.append(item)
            
        return items
        
    #Extract the classes that are separated by ;
    def ClassList (self, text ):
            class_list = []
            
            length = len(text)
            start_pos = 0
            end_pos   = 0
            while (start_pos < length):
                end_pos = text.find(";", start_pos)
                 
                if (end_pos < 0):
                    end_pos = length
                    
                class_list.append(text[start_pos:end_pos].strip())
                start_pos = end_pos +1
                
            return class_list
        
    def ExtractName(self, text ):
            #Trim non-characters and spaces
            char="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            length = len(text)
            start_pos = -1
            for i in range(0, length-1):
                if (char.find(text[i:i+1])>=0 and start_pos==-1): 
                    start_pos=i
            
            end_pos = -1
            for i in range(length-1, 0,-1):
                if (char.find(text[i:i+1])>=0 and end_pos==-1): 
                    end_pos=i
    
            new_str = text[start_pos:end_pos+1]
            length  = len(new_str)
            pos = new_str.find(";")
            if pos>=0:
                lastName  = new_str[0:pos].strip()
                firstName = new_str[pos+1:length].strip()
            else:
                lastName  =  new_str.strip()
                firstName = ""
            
            name_list = []
            name_list.append(firstName)
            name_list.append(lastName)
            return name_list
    
    #Extract the inventor's city, assuming text="(city, country)"
    def ExtractInvCity(self, text ):
        #Trim non-characters and spaces
        city_list = []
        
        start_pos = -1
        end_pos   = -1
        loc = 0
        while (True):
            #Find "(" and "," grab the city then find ")" to grab the country
            start_pos = text.find("(", loc)
            
            #Find the comma closest to the ")"
            rbraket_pos = text.find(")", start_pos)
            
            #If there is a comma, try to find one closest to ")"
            end_pos     = text.rfind(",", start_pos, rbraket_pos)
            if (start_pos >=0 and end_pos >=0):
                city_list.append(text[start_pos+1:end_pos].strip())
            else:
                break
            
            loc = end_pos + 1
        return city_list

    #Extract the inventor's country, assuming text="(city, country)"
    def ExtractInvCountry(self, text ):
        #Trim non-characters and spaces
        country_list = []
        
        start_pos = -1
        end_pos   = -1
        loc = 0
        while (True):
            #Find "(" and "," grab the city then find ")" to grab the country
            loc = text.find("(", loc)
            if (loc <0) : break
            start_pos = text.find(",", loc)
            
            #Sometimes there is no city so the comma will not show-up
            if (start_pos < 0) :
                start_pos = loc
            
            end_pos   = text.find(")", start_pos)
            
            #If there is a comma, try to find one closest to ")"
            if (start_pos<>loc):
                start_pos= text.rfind(",", loc, end_pos)
            
            if (start_pos >=0 and end_pos >=0):
                country_list.append(text[start_pos+1:end_pos].strip()) 
            else:
                break
            
            loc = end_pos + 1
        return country_list        
    
