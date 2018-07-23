from pymongo import MongoClient
from bson import json_util
import json
import sys 

finder = {}
list_referrers = False
if len(sys.argv) > 1:
    try:
        finder['http_code'] = int(sys.argv[1])
    except:
        finder['url'] = sys.argv[1]
        list_referrers = True
if len(sys.argv) > 2:
    if sys.argv[2] == 'True':
        list_referrers = True
scrape_collection = MongoClient().test.scrape
cursor = scrape_collection.find(finder)
documents = []
for document in cursor:    
    documents.append(document)
documents.sort(key=lambda obj: len(obj['referrer']))
for document in documents:
    print document['http_code'], len(document['referrer']), document['url'] 
    if list_referrers:
        for ref in document['referrer']:
            if ref.startswith('https://quickbooks.intuit.com/ca/resources'):
                print '    ', ref.replace('https://quickbooks.intuit.com/ca/resources', 'https://author.intuit.com/camentor')
            else:
                print '    ', ref
