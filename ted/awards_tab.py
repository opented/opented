from lxml import html
from pprint import pprint
import dateutil.parser
import dataset
from values import text_value

list_fields = dataset.connect('sqlite:///reference.db').get_table('list_fields')
list_fields_all = list(list_fields.all())


def text_html(field, el):
    return {field: html.tostring(el)}


def text_addr(field, el):
    addr = el.cssselect('.addr')
    if len(addr):
        el = addr.pop()
    name = plain = text_plain(field, el)[field]
    if '\n' in name:
        name, _ = name.split('\n', 1)
    return {field + '_name': name, field + '_addr': plain}


def text_plain(field, el):
    for br in el.findall('.//br'):
        br.text = '\n'
    text = el.text_content().strip()
    return {field: text}


def text_date(field, el):
    for br in el.findall('.//br'):
        br.text = '\n'
    text = el.text_content().strip()
    try:
        data = dateutil.parser.parse(text)
        value = data.strftime('%Y-%m-%d')
    except:
        value = text
    return {field: value}


FIELD_HANDLERS = {
    'description': text_plain,
    'tenderer': text_addr,
    'authority': text_addr,
    'contract_value': text_value,
    'total_value': text_value,
    'cpv': text_plain,
    'dac_code': text_plain,
    'award_date': text_date
}


def parse_mli(mli):
    key = None
    keys = mli.cssselect('span.timark')
    if len(keys):
        key = keys.pop().text
    text = mli.cssselect('.txtmark')
    if not len(text):
        return key, ''
    #assert len(text) == 1, text
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
            data.update(FIELD_HANDLERS.get(column, text_plain)(column, v))
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
            assert title.lower() == 'SECTION V: AWARD OF CONTRACT'.lower(), \
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
    #table.delete(uri=uri)
    for contract in parse_awards(doc):
        contract['uri'] = uri
        #pprint(contract)
        table.insert(contract)

