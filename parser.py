from pprint import pprint
from lxml import html
from common import traverse_local, as_document, generate_paths
from awards import parse_awards, extract_awards
from text import extract_plain

from optparse import OptionParser

import os
import dataset

DATA_CODES = {
    'TI': ('title', 'item'),
    'ND': ('document_number', 'item'),
    'PD': ('publication_date', 'item'),
    'OJ': ('oj', 'item'),
    'TW': ('place', 'item'),
    'AU': ('authority_name', 'item'),
    'OL': ('original_language', 'item'),
    'HD': ('heading', 'item'),
    'CY': ('country', 'item'),
    'AA': ('authority_type', 'code'),
    'DS': ('document_sent', 'item'),
    'DD': ('comment_deadline', 'item'),
    'DT': ('deadline', 'item'),
    'NC': ('contract', 'code'),
    'PR': ('procedure', 'code'),
    'TD': ('document', 'code'),
    'RP': ('regulation', 'code'),
    'TY': ('bid_type', 'code'),
    'AC': ('award_criteria', 'code'),
    'RC': ('nuts_code', 'item'),
    'DI': ('directive', 'item'),
    'PC': ('cpv_code', 'list'),
    'OC': ('cpv_original_code', 'list'),
    'IA': ('url', 'item'),
    }


def parse_current_language(path):
    print "PCL PATH ", path
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

def parse_data(path):
    data = {}
    cl = as_document(path)
    if cl is None:
        return data
    for row in cl.cssselect('#docContent tr'):
        code, title, value = row.getchildren()
        code, title = code.text, title.text
        if not code in DATA_CODES:
            print "Missing code spec:", path, code, [title]
            continue
        field, field_type = DATA_CODES[code]
        text = value.text
        if field_type == 'list':
            data[field] = [text] + [br.tail for br in value.findall('br')]
        elif field_type == 'code':
            id, name = text.split('-', 1)
            data[field + '_id'] = id.strip()
            data[field + '_name'] = name.strip()
        else:
            data[field] = text

    num, year = data.get('document_number').split('-')
    data['uri'] = 'TED:NOTICE:%s-%s:DATA:EN:HTML' % (num, year)

    return data


def parse_tender(engine, paths):
    print "PATHS ", paths

    lang_doc, data = parse_current_language(paths[0])
    data.update(parse_data(paths[3]))
    if not 'uri' in data:
        pprint(data)
        return

    if 'award' in data['heading'].lower():
        #print paths[0]
        #parse_awards(lang_doc)
        extract_awards(engine, data['uri'], lang_doc)
        #pprint(data)

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


if __name__ == '__main__':
    if "DATABASE" in os.environ:
        db_addr = os.environ['DATABASE']
    else:
        db_addr = 'postgresql://localhost/opented'

    p = OptionParser()
    p.add_option("--db", dest="database", default=db_addr)
    p.add_option("--year", dest="year", type=int, default=None)
    p.add_option("--num", dest="num", type=int, default=None)

    options, args = p.parse_args()

    engine = dataset.connect(options.database)

    if options.year and options.num:
        paths = generate_paths(options.year, options.num)
        if paths is not None:
            parse_tender(engine, paths)
    else:
        parse(engine)

