import requests
import os
from itertools import count

from threaded import threaded

session = requests.Session()

def init():
    global session
    session = requests.Session()
    session.get('http://www.ted.europa.eu/TED/browse/browseByBO.do')

def get(uri, tab):
    return session.get('http://www.ted.europa.eu/udl',
            params={'uri': uri, 'tabId': tab},
            allow_redirects=False,
            cookies={'lg': 'en'})

def tender_path(year, num, tab):
    hash_dir = int(str(num)[:3])
    path = 'tenders/%s/%03d/%s/tab_%s.html' % (year, hash_dir, num, tab)
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    return path

def get_entry(year, num):
    uri = 'TED:NOTICE:%s-%s:DATA:EN:HTML' % (num, year)
    print "URI", uri
    for tab in range(0, 4):
        path = tender_path(year, num, tab)
        if os.path.isfile(path):
            continue
        res = get(uri, tab)
        if tab == 0 and res.status_code != 200:
            if 'invalidUDLLink.do' in res.headers.get('location'):
                return False
            else:
                init()
                return get_entry(year, num)
        if res.status_code == 200:
            fh = open(path, 'wb')
            fh.write(res.content)
            fh.close()
    return True

def all_entries(year):
    for num in count(1):
        if not get_entry(year, num):
            break

def all_years():
    for year in range(2009, 2014):
        all_entries(year)

if __name__ == '__main__':
    init()
    threaded(range(2009, 2014), all_entries)
    #all_years()





