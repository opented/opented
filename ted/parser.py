import logging
from pprint import pprint
from lxml import html
from common import traverse_local, as_document, generate_paths
from common import get_engine
from awards_tab import parse_awards, extract_awards
from data_tab import parse_data
from text import extract_plain
from threaded import threaded

from optparse import OptionParser

import os
import dataset

log = logging.getLogger(__name__)


def parse_current_language(path):
    cl = as_document(path)
    data = {'source_tender': path.rsplit('/', 1)[0]}
    data['title_uc'] = cl.cssselect('#mainContent h2').pop().text
    content = cl.cssselect('#docContent').pop()
    data['date'] = content.cssselect('#docHeader span.date').pop().text
    data['oj_uc'] = content.cssselect('#docHeader span.oj').pop().text
    data['heading'] = content.cssselect('#docHeader span.heading').pop().text.strip()
    signature, identifier = content.cssselect('.tab > div.stdoc p')
    #org, org_identifier, org_type, org_regulation = stddocs
    data['signature'] = signature.text
    data['identifier'] = identifier.text

    return cl, data


def parse_tender(engine, paths):
    #print "PATHS ", paths

    lang_doc, data = parse_current_language(paths[0])
    data.update(parse_data(paths[3]))
    if not 'uri' in data:
        #pprint(data)
        return

    if 'award' in data['heading'].lower():
        #try:
        extract_awards(engine, data['uri'], lang_doc)
        #except Exception, e:
        #    print [e]

    print data['uri']

    # find out what this is good for :)
    if 'cpv_original_code' in data:
        del data['cpv_original_code']

    for cpv_link in data.pop('cpv_code'):
        cpv_code, cpv_title = cpv_link.split(' - ')
        engine['document_cpv'].upsert({
            'document_uri': data['uri'],
            'code': cpv_code,
            'title': cpv_title }, ['document_uri', 'code'])
    engine['document'].upsert(data, ['uri'])
    extract_plain(engine, data['uri'], lang_doc)
    #print data['uri']

def parse(engine):
    for paths in traverse_local():
        parse_tender(engine, paths)

def parse_threaded(engine):
    def fnc(p):
        try:
            parse_tender(engine, p)
        except Exception, e:
            log.exception(e)
    threaded(traverse_local(), fnc, num_threads=20)


if __name__ == '__main__':

    p = OptionParser()
    p.add_option("--year", dest="year", type=int, default=None)
    p.add_option("--num", dest="num", type=int, default=None)

    options, args = p.parse_args()
    engine = get_engine()

    if options.year and options.num:
        paths = generate_paths(options.year, options.num)
        if paths is not None:
            parse_tender(engine, paths)
    else:
        parse_threaded(engine)

