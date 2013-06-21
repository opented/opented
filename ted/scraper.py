import requests
import os
from itertools import count

from optparse import OptionParser
from threaded import threaded
from common import tender_path, FAILURES

session = requests.Session()


def make_session():
    global session
    session = requests.Session()
    session.get('http://www.ted.europa.eu/TED/browse/browseByBO.do')


def get(uri, tab):
    return session.get('http://www.ted.europa.eu/udl',
                       params={'uri': uri, 'tabId': tab},
                       allow_redirects=False,
                       cookies={'lg': 'en'})


def get_entry(year, num):
    uri = 'TED:NOTICE:%s-%s:DATA:EN:HTML' % (num, year)
    print "URI", uri
    for tab in range(0, 5):
        path = tender_path(year, num, tab)
        if os.path.isfile(path):
            continue
        res = get(uri, tab)
        if tab == 0 and res.status_code != 200:
            if 'invalidUDLLink.do' in res.headers.get('location'):
                return False
            else:
                make_session()
                return get_entry(year, num)
        if res.status_code == 200:
            fh = open(path, 'wb')
            fh.write(res.content)
            fh.close()
    return True


def all_entries(year, offset=1):
    failed = 0
    for num in count(offset):
        if not get_entry(year, num):
            failed += 1
        else:
            failed = 0
        if failed > FAILURES:
            break


def all_years():
    for year in range(2009, 2014):
        all_entries(year)


if __name__ == '__main__':
    make_session()

    p = OptionParser()
    p.add_option("--year", dest="year", type=int, default=None)

    options, args = p.parse_args()
    if options.year:
        all_entries(options.year)
    else:
        threaded(range(2009, 2014), all_entries)
