import decimal
import hashlib 
import re

swkey = 'swkey'
tmp_dir = '/tmp/'

def digest(d):
    return hashlib.sha224(d).hexdigest()
 

# mail format - critical but discoverable 
dt_split_format = '%Y_%m_%d/%H_%M_%S'
dt_single_format = '%Y_%m_%d_%H_%M_%S'


email_filename = '(.*?)"(.*?)"'

NO_SUBJECT = "(no subject)"

def simplify_to_id(inp):    
    step1 = re.sub(r" ", r"_", inp.strip().lower().replace('.', '').replace('/', '').replace(',', '').replace('-', ' ').replace('  ', ' '))
    return re.sub(r"__", r"_", step1)

def simpleurl(url):
    from urlparse import urlparse
    if not urlparse(url).scheme:
            return "http://" + url                            
    return url

def item_to_dict(item_or_items, filter_key = None):
    def single_element(item):
        def check_value(value):
            if isinstance(value, decimal.Decimal):
                return int(value)
            if isinstance(value, set):
                return list(value)
            return value
        try:
            return dict((key, check_value(item[key])) for key in [key for key in item.keys() if filter_key is None or key in filter_key])
        except AttributeError as e:
            # print 'warning item to dict'
            return {}
    if isinstance(item_or_items, list):
        return [single_element(item) for item in item_or_items]
    else:
        return single_element(item_or_items)

def blank_msg():
    return { 
        'msg': None,
        'derived_to': None,
        'derived_from': None,
        'to': None,
        'from': None,
        'subject': None,
        'helo': None,
        'attachments' : None,
        'multipart' : None,
        'origin': None,
        'user': None,
        'date': None
    }        

def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def numTwitter(tn):
    if not tn:
        return '0'
    elif tn / 1000000 >= 1:
        return '' + str(tn / 1000000) + '.' + str((tn % 1000000)/10000) + 'M';
    elif tn / 1000 >= 100:
        return '' + str(tn / 1000) + 'K';
    elif tn / 1000 >= 10:
        return '' + str(tn / 1000) + 'K';    
    elif tn / 1000 >= 1:
        return '' + str(tn / 1000) + ',' + str(tn % 1000);
    else:
        return '' + str(tn)


_placeholder = '_place_holder_'
html_placeholder = '<span>' + _placeholder + '</span>'

def twitterToNum(v):
    if not v:
        return 0;
    if ',' in v:
        v = re.sub(r',', '', v)
    if 'M' in v:
        v = re.sub(r'M', '', v)
        return int(float(v) * 1000000)
    if 'K' in v:
        v = re.sub(r'K', '', v)
        return int(float(v) * 1000)
    return int(v)

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}