# -*- coding: utf-8 -*-
"""Helper functions for patent processing"""
import os
import sys

import difflib

class PatentData(object):
    """ Various functions for cleansing patent extracted data. """ 
    def __init__(self):
        pass
    
    def check_string_diff_ratio(self, a,b):
        ''' 
        Returns a value [0,1] that corresponds to how similar the strings
        are to each other.
        '''
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


class PatentUtil(object):
    """ General utility functions for patent scraping. """ 
        
    def generate_us_patent_urls(self):
        ''' 
        Generate a list of start URLs for the Spider based on predefined
        search terms. Outputs text file used by Spider for crawling. 
        '''        
        search_terms = self.define_search_terms()
        
        # cycle through all search terms to create start url list
        start_url = "http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&p=1&f=S&l=50&Query="
        end_url = "&d=PTXT"
        
        search_url_list = []
        for i in range(len(search_terms)):
            search_terms[i] = search_terms[i].replace("/", "%2f")
            search_terms[i] = search_terms[i].replace("(", "%28")
            search_terms[i] = search_terms[i].replace(")", "%29")
            search_terms[i] = search_terms[i].replace(" ", "+")
            search_url_list.append(start_url + search_terms[i] + end_url + "\n")
         
        return search_url_list
    
    def define_search_terms(self):
        '''
        Function that returns a list of all hardcoded search terms.
        '''
        search_term_list = []
        
        search_term_list.append("abst/(quantum and (error) and (correction or correcting))")        
        search_term_list.append("abst/(qubit or qubits)")        
        search_term_list.append("abst/(single and photon)")
        search_term_list.append("abst/(quantum and (computation or computing or computer))")
        search_term_list.append("abst/(quantum and (entangled or entanglement or entangling))")
        search_term_list.append("abst/(quantum and (single-photon))")
        search_term_list.append("abst/(quantum and (key or keys or cipher))")
        search_term_list.append("abst/(quantum and (information))")
        search_term_list.append("abst/(quantum and (communication))")
        search_term_list.append("abst/(quantum and (random) and (number))")
        search_term_list.append("abst/(quantum and (encryption or cryptography or cryptographic))")
        search_term_list.append("abst/(polarization and (entangled) and (photon or photons))")
        search_term_list.append("abst/(polarization-entangled)")
        search_term_list.append("abst/(quantum and (qkd))")
        search_term_list.append("abst/(quantum and (repeater))")
        search_term_list.append("abst/(entangled and (photon) and (source))")
        search_term_list.append("abst/(entangled and (particles or systems or states or state))")
        search_term_list.append("abst/(quantum and (nitrogen or NV) and (center or centers))")
        search_term_list.append("abst/(quantum and (single) and (photon) and (detector))")
        search_term_list.append("abst/(quantum and (superposition))")
                    
        return search_term_list
        
        
    def write_file(self, file_name, file_ext, content):
        '''
        Write file of specified extension in local directory. 
        '''
        if "." not in file_ext:
            file_ext = "." + file_ext
        print ("Writing file %s%s...") % (file_name, file_ext)
        with open(file_name+file_ext, 'w') as out_file:
            out_file.write(content)
        print ("Done.")
        
        
    def list_2_str(self, _list):
        '''Converts a list of objects into a concatenation of strings.'''
        return ' '.join(map(str, _list))        
        
#p = PatentUtil()
#search_list = p.generate_us_patent_urls()
#search_terms_content = ""
#for i in range(len(search_list)):
#    search_terms_content += search_list[i]
#    
#p.write_file('test','.txt',search_terms_content)

#q = PatentData()
#print q.check_string_diff_ratio("D Wave Systems","D-Wave Corporation")