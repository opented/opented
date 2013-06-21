import logging
from datetime import datetime

from common import get_engine, traverse_local
from threaded import threaded
from scraper import all_entries
from parser import parse_tender


QUERY = r"SELECT MAX(REGEXP_REPLACE(document_number, '^(\d*)-(\d*)$', '\2-\1')) FROM document;"


def update():
    engine = get_engine()
    q = engine.query(QUERY).next()
    if not len(q.keys()):
        return
    next = q.values().pop()
    year, num = next.split('-')
    years = range(int(year), datetime.now().year+1)
    offsets = [int(num)] + ([0] * len(years))
    print "CONTINUING", zip(years, offsets)
    for year, offset in zip(years, offsets):
        all_entries(year, offset=offset)
        for paths in traverse_local([year], offset):
            parse_tender(engine, paths)


if __name__ == '__main__':
    update()
