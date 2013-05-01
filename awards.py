from lxml import html
from pprint import pprint

import dataset

list_fields = dataset.connect('sqlite:///reference.db').get_table('list_fields')
list_fields_all = list(list_fields.all())

def text_html(field, el):
    return {field: html.tostring(el)}

def text_plain(field, el):
    for br in el.findall('.//br'):
        br.text = '\n'
    text = el.text_content().strip()
    return {field: text}

def text_value(field, el):
    data = {}
    cur_field = field
    plain = text_plain(field, el)[field]
    for line in plain.split('\n'):
        lline = line.lower()
        if lline.startswith('value '):
            data[cur_field] = line[6:]
        elif 'vat' in lline or lline.startswith('including') or \
            lline.startswith('excluding'):
            data[cur_field + '_vat'] = line
        elif 'total final value' in lline:
            cur_field = field + '_final'
        elif 'initial estimated total value' in lline:
            cur_field = field + '_initial'
        elif 'annual or monthly' in lline:
            data[cur_field + '_term'] = line
        else:
            print plain.split('\n')
    return data

def text_addr(field, el):
    name = plain = text_plain(field, el)[field]
    if '\n' in name:
        name, _ = name.split('\n', 1)
    return {field + '_name': name, field + '_addr': plain}

FIELD_HANDLERS = {
    'description': text_plain,
    'tenderer': text_addr,
    'authority': text_addr,
    'value': text_value,
    'total_value': text_value,
    'cpv': text_plain,
    'dac_code': text_plain
    }

def parse_mli(mli):
    key = None
    keys = mli.cssselect('span.timark')
    if len(keys):
        key = keys.pop().text
    text = mli.cssselect('.txtmark')
    if not len(text):
        return key, ''
    assert len(text)==1, text
    return key, text.pop()
    

def parse_list(el):
    data = {}
    for mli in el.findall('./div[@class="mlioccur"]'):
        k, v = parse_mli(mli)
        if not len(v) or k is None:
            continue
        column = None
        for lf in list_fields_all:
            if lf.get('field') == k:
                column = lf.get('column')
        if column is not None:
            data.update(FIELD_HANDLERS.get(column, text_html)(column, v))
        else:
            list_fields.upsert({'field': k}, ['field'])
    return data

def parse_awards(doc):
    body = doc.find('.//div[@class="DocumentBody"]')
    data = parse_list(body)
    contracts = []
    title = None
    for seq in body.findall('./*[@class="grseq"]'):
        titles = seq.cssselect('.tigrseq')
        if len(titles):
            title = titles.pop().xpath('string()')
        section = parse_list(seq)
        subtitle = seq.find('./span')
        if subtitle is not None:
            subtitle = subtitle.text
            assert title.lower()=='SECTION V: AWARD OF CONTRACT'.lower(), \
                [title, subtitle]
            section['contract_id'] = subtitle
            contracts.append(section)
        else:
            data.update(section)
    
    if not len(contracts):
        yield data
    else:
        for contract in contracts:
            contract.update(data)
            yield contract

def extract_awards(engine, uri, doc):
    table = engine['awards']
    table.delete(uri=uri)
    contracts = []
    for contract in parse_awards(doc):
        contract['uri'] = uri
        pprint(contract)
        table.insert(contract)



