from scrapy.spider import CrawlSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import  Rule
from scrapy.linkextractor import LinkExtractor
from urlparse import urlparse
from goose import Goose
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class MySpider(CrawlSpider):
   name = "nell"
   allowed_domains = ["kompas.com"]
   response_url = ""

   start_urls = ["http://news.kompas.com"]
   rules = (
      Rule(LinkExtractor(allow=[r'/read/2017',r'/read/2016']), callback='parse_items', follow=True),
   )

   def __init__(self, *a, **kw):
      super(MySpider, self).__init__(*a, **kw)
      self.current_dir_name  = os.path.dirname(os.path.abspath(__file__))
      self.raw_data_dir_name = self.current_dir_name+"/raw_data"
      self.extracted_data_dir_name = self.current_dir_name+"/extracted_data"

      self.extractor = Goose({'use_meta_language': False, 'target_language':'id'})

      if not os.path.exists(self.raw_data_dir_name):
         print "CREATING DIRECTORIES :", 
         os.makedirs(self.raw_data_dir_name)
         os.makedirs(self.extracted_data_dir_name)

    # This spider has one rule: extract all (unique and canonicalized) links, follow them and parse them using the parse_items method

   def filter_links(self, links):
      baseDomain = self.get_base_domain( self.response_url)
      filteredLinks = []
      for link in links:
         if link.url.find(baseDomain) < 0:
            filteredLinks.append(link)
      return filteredLinks

   def get_base_domain(self, url):
      base = urlparse(url).netloc
      if base.upper().startswith("WWW."):
         base = base[4:]
      elif base.upper().startswith("FTP."):
         base = base[4:]
         # drop any ports
      base = base.split(':')[0]

      return base

   def parse_items(self, response):
      print "CURRENT DIR NAME ",self.current_dir_name
      
      raw_filename = self.raw_data_dir_name+"/"+response.url.split("/")[-1].replace('.html','') + '.html'
      with open(raw_filename, 'wb') as f:
         f.write(response.body) # DUMP raw data

      extracted_text = self.extractor.extract(raw_html=response.body)

      extracted_text_filename = self.extracted_data_dir_name+"/"+response.url.split("/")[-1].replace('html','') + '.txt'
      with open(extracted_text_filename,'wb') as f:
        f.write(extracted_text.cleaned_text)
