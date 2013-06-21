import os
from itertools import count
from lxml import html

import dataset

FAILURES = 5000

def get_engine():
    if "DATABASE" in os.environ:
        db_addr = os.environ['DATABASE']
    else:
        db_addr = 'postgresql://localhost/opented'
    return dataset.connect(db_addr)


def tender_path(year, num, tab, create=True):
    hash_dir = int(str(num)[:3])
    path = 'tenders/%s/%03d/%s/tab_%s.html' % (year, hash_dir, num, tab)
    dirname = os.path.dirname(path)
    if create and not os.path.isdir(dirname):
        os.makedirs(dirname)
    return path

def generate_paths(year, num):
    path = tender_path(year, num, 0, create=False)
    if not os.path.isfile(path):
        return None
    dir_base = os.path.dirname(path)
    pattern = dir_base + '/tab_%s.html'
    return [pattern % i for i in range(0, 4)]

def traverse_local():
    for year in range(2009, 2014):
        fails = FAILURES
        for num in count(1):
            paths = generate_paths(year, num)
            if paths is None:
                fails -= 1
                if fails <= 0:
                    break
            if paths is not None:
                fails = FAILURES
                yield paths

def as_document(path):
    try:
        fh = open(path, 'rb')
        doc = html.fromstring(fh.read().split('\r\n', 1)[-1])
        fh.close()
        return doc
    except IOError:
        return None

def get_output_dir():
    return 'site/'

def list_years(**filters):
    document = get_engine()['document']
    return [y['year'] for y in document.distinct('year', **filters)]

def list_countries(**filters):
    document = get_engine()['document']
    return [c['country'] for c in document.distinct('country', **filters)]
