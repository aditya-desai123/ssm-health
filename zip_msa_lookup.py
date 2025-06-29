import requests
import pandas as pd
import time
from typing import Dict, Optional
import json
import re

class ZipMSALookup:
    def __init__(self):
        """Initialize the MSA lookup system using the public ZIP-to-MSA API"""
        self.msa_cache = {}
        # Try both HTTP and HTTPS endpoints
        self.api_base_urls = [
            "https://zip-to-msa-api-prod.mjr2sdfatp.us-west-2.elasticbeanstalk.com",
            "http://zip-to-msa-api-prod.mjr2sdfatp.us-west-2.elasticbeanstalk.com"
        ]
        self.api_working = None  # Will be set when we test the API
        
        # Fallback mapping for when API is not available
        self.fallback_mapping = {
            # Illinois MSAs - basic fallback
            ('Chicago', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Naperville', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Elgin', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Aurora', 'IL'): 'Chicago-Naperville-Elgin, IL-IN-WI',
            ('Rockford', 'IL'): 'Rockford, IL',
            ('Peoria', 'IL'): 'Peoria, IL',
            ('Springfield', 'IL'): 'Springfield, IL',
            ('Champaign', 'IL'): 'Champaign-Urbana, IL',
            ('Urbana', 'IL'): 'Champaign-Urbana, IL',
            ('Bloomington', 'IL'): 'Bloomington, IL',
            ('Normal', 'IL'): 'Bloomington, IL',
            ('Decatur', 'IL'): 'Decatur, IL',
            ('Carbondale', 'IL'): 'Carbondale-Marion, IL',
            ('Marion', 'IL'): 'Carbondale-Marion, IL',
            ('Quincy', 'IL'): 'Quincy, IL-MO',
            ('Danville', 'IL'): 'Danville, IL',
            ('Kankakee', 'IL'): 'Kankakee, IL',
            ('Ottawa', 'IL'): 'Ottawa-Peru, IL',
            ('Peru', 'IL'): 'Ottawa-Peru, IL',
            ('Dixon', 'IL'): 'Dixon, IL',
            ('Sterling', 'IL'): 'Sterling, IL',
            ('Rock Island', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('Moline', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('East Moline', 'IL'): 'Davenport-Moline-Rock Island, IA-IL',
            ('Galesburg', 'IL'): 'Galesburg, IL',
            ('Macomb', 'IL'): 'Macomb, IL',
            ('Freeport', 'IL'): 'Freeport, IL',
        }
        
        # ZIP code to MSA mapping for Illinois (fallback when API is not available)
        self.zip_msa_mapping = {
            # Chicago area ZIP codes
            '60601': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60602': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60603': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60604': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60605': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60606': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60607': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60608': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60609': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60610': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60611': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60612': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60613': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60614': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60615': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60616': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60617': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60618': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60619': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60620': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60621': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60622': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60623': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60624': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60625': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60626': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60628': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60629': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60630': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60631': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60632': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60633': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60634': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60636': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60637': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60638': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60639': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60640': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60641': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60642': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60643': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60644': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60645': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60646': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60647': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60649': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60651': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60652': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60653': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60654': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60655': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60656': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60657': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60659': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60660': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60661': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60664': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60666': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60668': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60669': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60670': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60673': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60674': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60675': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60677': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60678': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60680': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60681': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60682': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60684': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60685': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60686': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60687': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60688': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60689': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60690': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60691': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60693': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60694': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60695': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60696': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60697': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            '60699': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},
            
            # Suburban Chicago ZIP codes
            '60007': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Elk Grove Village
            '60008': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Rolling Meadows
            '60010': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Barrington
            '60015': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Deerfield
            '60016': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Des Plaines
            '60018': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Glenview
            '60025': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Glencoe
            '60026': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Highland Park
            '60029': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Libertyville
            '60035': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Lake Forest
            '60043': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Kenilworth
            '60045': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Lake Bluff
            '60053': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Mount Prospect
            '60056': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Mount Prospect
            '60062': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Northbrook
            '60067': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Palatine
            '60068': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Palatine
            '60069': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Palatine
            '60074': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Park Ridge
            '60076': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Prospect Heights
            '60077': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Rolling Meadows
            '60084': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60085': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60089': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60090': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60091': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60092': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60093': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60094': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60095': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60096': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60097': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60098': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            '60099': {'msa_name': 'Chicago-Naperville-Elgin, IL-IN-WI', 'msa_code': '16980'},  # Schaumburg
            
            # Other Illinois MSAs
            '61101': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61102': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61103': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61104': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61105': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61106': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61107': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61108': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61109': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61110': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61111': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61112': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61114': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61115': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61125': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            '61126': {'msa_name': 'Rockford, IL', 'msa_code': '40340'},  # Rockford
            
            '61601': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61602': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61603': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61604': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61605': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61606': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61607': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61610': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61611': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61612': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61613': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61614': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61615': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61616': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61625': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61629': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61630': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61633': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61634': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61636': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61637': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61638': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61639': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61641': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61643': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61650': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61651': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61652': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61653': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61654': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61655': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            '61656': {'msa_name': 'Peoria, IL', 'msa_code': '37900'},  # Peoria
            
            '62701': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62702': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62703': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62704': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62705': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62706': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62707': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62708': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62709': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62711': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62712': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62713': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62715': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62716': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62719': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62721': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62722': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62723': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62726': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62736': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62739': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62746': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62756': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62757': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62761': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62762': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62763': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62764': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62765': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62766': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62767': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62769': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62776': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62777': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62781': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62786': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62791': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62794': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
            '62796': {'msa_name': 'Springfield, IL', 'msa_code': '44100'},  # Springfield
        }
    
    def get_zip_from_address(self, address: str) -> Optional[str]:
        """
        Extract ZIP code from address string
        
        Args:
            address (str): Full address string
            
        Returns:
            str: ZIP code or None if not found
        """
        if not address or address == 'N/A':
            return None
        
        # Try to extract ZIP from address
        # Common format: "Street, City, State ZIP"
        parts = address.split(',')
        if len(parts) >= 3:
            state_zip = parts[2].strip()
            # Extract ZIP (last 5 digits)
            words = state_zip.split()
            for word in words:
                if len(word) == 5 and word.isdigit():
                    return word
        
        # Alternative: look for 5-digit number anywhere in the address
        zip_match = re.search(r'\b\d{5}\b', address)
        if zip_match:
            return zip_match.group()
        
        return None
    
    def get_msa_from_zip_api(self, zip_code: str) -> Dict:
        """
        Get MSA data from the public ZIP-to-MSA API using ZIP code
        
        Args:
            zip_code (str): 5-digit ZIP code
            
        Returns:
            Dict: MSA data from API
        """
        # Check cache first
        if zip_code in self.msa_cache:
            return self.msa_cache[zip_code]
        
        # If we know the API is not working, skip the API call
        if self.api_working is False:
            return self._get_fallback_msa_data(zip_code)
        
        try:
            # Try each API endpoint
            for api_base_url in self.api_base_urls:
                try:
                    url = f"{api_base_url}/api"
                    
                    params = {
                        'zip': zip_code
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # The API returns: zip, cbsa, msaName, population2014, population2015
                        if data and 'msaName' in data:
                            msa_data = {
                                'msa_name': data['msaName'],
                                'msa_code': data.get('cbsa', '00000'),
                                'zip_code': zip_code,
                                'population_2014': data.get('population2014', 'N/A'),
                                'population_2015': data.get('population2015', 'N/A'),
                                'source': 'Public ZIP-to-MSA API'
                            }
                            
                            # Cache the result
                            self.msa_cache[zip_code] = msa_data
                            self.api_working = True  # Mark API as working
                            return msa_data
                    
                except Exception as e:
                    print(f"Error with endpoint {api_base_url}: {e}")
                    continue
            
            # If we get here, none of the API endpoints worked
            self.api_working = False
            return self._get_fallback_msa_data(zip_code)
            
        except Exception as e:
            print(f"Error calling ZIP-to-MSA API: {e}")
            self.api_working = False
            return self._get_fallback_msa_data(zip_code)
    
    def _get_fallback_msa_data(self, zip_code: str = None) -> Dict:
        """
        Get fallback MSA data when API is not available
        
        Args:
            zip_code (str): ZIP code to look up in fallback mapping
            
        Returns:
            Dict: Fallback MSA data
        """
        # If we have a ZIP code, try the fallback mapping first
        if zip_code and zip_code in self.zip_msa_mapping:
            msa_info = self.zip_msa_mapping[zip_code]
            return {
                'msa_name': msa_info['msa_name'],
                'msa_code': msa_info['msa_code'],
                'zip_code': zip_code,
                'population_2014': 'N/A',
                'population_2015': 'N/A',
                'source': 'ZIP Code Fallback Mapping'
            }
        
        return {
            'msa_name': 'Unknown',
            'msa_code': '00000',
            'zip_code': zip_code,
            'population_2014': 'N/A',
            'population_2015': 'N/A',
            'source': 'Fallback'
        }
    
    def get_msa(self, city: str, state: str, zip_code: str = None) -> Dict:
        """
        Get MSA data for a given city, state, and optionally ZIP code
        
        Args:
            city (str): City name
            state (str): State abbreviation
            zip_code (str): ZIP code (optional)
            
        Returns:
            Dict: MSA data
        """
        # Normalize the input
        city = city.strip().title()
        state = state.strip().upper()
        
        # Check cache first
        cache_key = f"{city}, {state}, {zip_code}"
        if cache_key in self.msa_cache:
            return self.msa_cache[cache_key]
        
        # If we have a ZIP code, try the API first
        if zip_code:
            msa_data = self.get_msa_from_zip_api(zip_code)
            if msa_data['msa_name'] != 'Unknown':
                self.msa_cache[cache_key] = msa_data
                return msa_data
        
        # Fallback to city/state mapping
        msa_name = self.fallback_mapping.get((city, state), 'Unknown')
        msa_data = {
            'msa_name': msa_name,
            'msa_code': '00000',
            'zip_code': zip_code,
            'population_2014': 'N/A',
            'population_2015': 'N/A',
            'source': 'Fallback Mapping'
        }
        
        self.msa_cache[cache_key] = msa_data
        return msa_data
    
    def get_msa_from_address(self, address: str) -> Dict:
        """
        Extract ZIP code from address and get MSA data
        
        Args:
            address (str): Full address string
            
        Returns:
            Dict: MSA data
        """
        if not address or address == 'N/A':
            return self._get_fallback_msa_data()
        
        # Extract ZIP code from address
        zip_code = self.get_zip_from_address(address)
        
        if zip_code:
            return self.get_msa_from_zip_api(zip_code)
        
        # Try to extract city and state as fallback
        parts = address.split(',')
        if len(parts) >= 3:
            city = parts[1].strip()
            state_zip = parts[2].strip()
            state = state_zip[:2].strip()
            return self.get_msa(city, state)
        
        return self._get_fallback_msa_data()
    
    def add_msa_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add MSA columns to a pandas DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame with address or city/state/zip columns
            
        Returns:
            pd.DataFrame: DataFrame with added MSA columns
        """
        # Try to extract ZIP codes from addresses if zip column doesn't exist
        if 'zip' not in df.columns and 'address' in df.columns:
            df['zip'] = df['address'].apply(self.get_zip_from_address)
        
        if 'city' in df.columns and 'state' in df.columns:
            # Get MSA data for each row
            msa_data_list = df.apply(
                lambda row: self.get_msa(
                    row['city'], 
                    row['state'], 
                    row.get('zip', None)
                ), 
                axis=1
            )
        elif 'address' in df.columns:
            # Get MSA data for each row using address
            msa_data_list = df['address'].apply(self.get_msa_from_address)
        else:
            # Set default values
            msa_data_list = [self._get_fallback_msa_data()] * len(df)
        
        # Extract individual fields
        df['msa'] = msa_data_list.apply(lambda x: x['msa_name'])
        df['msa_code'] = msa_data_list.apply(lambda x: x['msa_code'])
        df['msa_source'] = msa_data_list.apply(lambda x: x['source'])
        df['population_2014'] = msa_data_list.apply(lambda x: x.get('population_2014', 'N/A'))
        df['population_2015'] = msa_data_list.apply(lambda x: x.get('population_2015', 'N/A'))
        
        return df
    
    def test_api_connection(self) -> bool:
        """
        Test if the public API is accessible
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Test with a known ZIP code (Chicago)
            test_zip = "60622"
            msa_data = self.get_msa_from_zip_api(test_zip)
            return msa_data['source'] == 'Public ZIP-to-MSA API'
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False
    
    def get_api_info(self) -> str:
        """
        Get information about the API being used
        
        Returns:
            str: API information
        """
        return """
Using the Public ZIP-to-MSA API from GitHub:
- Repository: https://github.com/vartanovs/zip-to-msa-api
- Public API URL: http://zip-to-msa-api-prod.mjr2sdfatp.us-west-2.elasticbeanstalk.com
- No API key required
- Provides: ZIP, CBSA code, MSA name, population data (2014-2015)

The API returns:
- zip: 5-digit ZIP code
- cbsa: Core Based Statistical Area code
- msaName: Metropolitan Statistical Area name
- population2014: Population in 2014
- population2015: Population in 2015

This is much simpler than the HUD API and doesn't require authentication!
""" 