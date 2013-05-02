from lxml import html
from pprint import pprint
import re

import dataset
import dateutil.parser

list_fields = dataset.connect('sqlite:///reference.db').get_table('list_fields')
list_fields_all = list(list_fields.all())

MONEY_RE = re.compile('[ \d,\.]+ [A-Z]{3}')
CCY_AT_THE_END = re.compile('[\d,\.]+[A-Z]{3}')

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
    value_columns = ('value ', 'value: ', 'amount ', 'value of the contract: ',)
    for line in plain.split('\n'):
        lline = line.lower()
        if not len(lline):
            continue
        elif lline.startswith(value_columns):
            for vc in value_columns:
                if lline.startswith(vc):
                    data.update(money_value(cur_field, None, line[len(vc):]))
                    break
        elif lline.startswith('lowest offer '):
            """
            E.g.
            Lowest offer 566 909,62 and highest offer 662 717,50 PLN
            """
            sline = line[len('Lowest offer '):]
            first, last = sline.split('and highest offer', 1)
            lower_value = first.strip().replace(' ', '').replace(',', '.')
            higher_value, higher_currency = money_from_string(last.replace('-',''))
            lower_currency = higher_currency
            data.update({
                '%s_%s_%s' % (cur_field, 'higher', 'value'): higher_value,
                '%s_%s_%s' % (cur_field, 'higher', 'currency'): higher_currency,
                '%s_%s_%s' % (cur_field, 'lower', 'value'): lower_value,
                '%s_%s_%s' % (cur_field, 'lower', 'currency'): lower_currency
            })
        elif ('vat' in lline or lline.startswith('including') or
                lline.startswith('excluding')):
            data[cur_field + '_vat'] = line
        elif 'contract no' in lline or 'contract number' in lline:
            data['contract_nr'] = line
        elif 'lot no' in lline:
            data['lot_nr'] = line
        elif 'total final value' in lline:
            cur_field = field + '_final'
        elif 'initial estimated total value' in lline:
            cur_field = field + '_initial'
        elif 'annual or monthly' in lline:
            data[cur_field + '_term'] = line
        elif 'number of months' in lline or 'number of years' in lline:
            data[cur_field + '_term'] = line
        elif MONEY_RE.match(line):
            tempvalue, tempccy = money_from_string(line)
            data.update({
                    field: tempvalue,
                    field+'_currency': tempccy
                }
                )
        elif line.startswith('Lot'):
            tempvalue, tempccy = money_from_string(lline.split(':')[1])
#            print 'Lot line: %s -- %s -- %s' % (line, tempvalue, tempccy)
            data.setdefault(field, 0)
            data[field] += tempvalue
            data.update({
                    field+'_currency': tempccy
                }
                )      
        else:
            data.update({
                    field: -1,
                    field+'_currency': 'XXX'
                }
                ) 
    return data


def text_addr(field, el):
    name = plain = text_plain(field, el)[field]
    if '\n' in name:
        name, _ = name.split('\n', 1)
    return {field + '_name': name, field + '_addr': plain}


def money_value(field, el=None, value=None):
    if value is None:
        value = text_plain(field, el)[field]
    value, currency = money_from_string(value)
    return {field: value, field + '_currency': currency}


def money_from_string(s):
    cleans = s.strip().replace(' ', '').replace('.','').replace(',', '.')
    try:
        if CCY_AT_THE_END.match(cleans):
            currency = cleans[-3:]
        else:
            currency = cleans[:3]   
    except ValueError:
       currency = 'XXX'
    try:
        if CCY_AT_THE_END.match(cleans):
            value = float(cleans[:-3])
        else:
            value = float(cleans[3:])      
    except ValueError:
        value = -1
    return value, currency


def award_date(field, el):
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
    'value': text_value,
    'total_value': text_value,
    'cpv': text_plain,
    'dac_code': text_plain,
    'award_date': award_date
}


def parse_mli(mli):
    key = None
    keys = mli.cssselect('span.timark')
    if len(keys):
        key = keys.pop().text
    text = mli.cssselect('.txtmark')
    if not len(text):
        return key, ''
    assert len(text) == 1, text
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
    table.delete(uri=uri)
    for contract in parse_awards(doc):
        contract['uri'] = uri
        #pprint(contract)
        table.insert(contract)
