import re
from pprint import pprint

NUMRE = '\d[\. \d]*(,\d{1,2})?'
CURRE = '(HT )?(?P<cur>[A-Z]{3})'

VALUE_LINE_RE = re.compile('^(Value|Amount|Value of the contract):?\s*(?P<val>' + \
        NUMRE+')\s*'+CURRE, re.M)
RANGE_LINE_RE = re.compile('^Lowest offer (?P<lo>'+NUMRE+') and highest ' + \
        'offer (?P<hi>(\-|'+NUMRE+')) '+CURRE)
VAT_LINE_RE = re.compile('^(Excluding VAT|Including VAT).*')

MONEY_RE = re.compile('[ \d,\.]+ [A-Z]{3}')
CCY_AT_THE_END = re.compile('[\d,\.]+[A-Z]{3}')

def to_number(value):
    value = value.replace(' ', '').replace('.', '').replace(',', '.')
    return float(value)

def text_value(field, el):
    from awards_tab import text_plain
    plain = text_plain(field, el)[field]
    return _text_value(field, plain.split('\n'))

def _text_value(field, lines):
    for line in lines:
        m = VAT_LINE_RE.match(line)
        if m is not None:
            #print [line, m.groups()]
            continue
        m = VALUE_LINE_RE.match(line)
        if m is not None:
            #print [line, to_number(m.group('val'))]
            continue
        m = RANGE_LINE_RE.match(line)
        if m is not None:
            #print [line, to_number(m.group('val'))]
            continue
        print 'XXX', lines
    return {}

def old_text_value(field, lines):
    data = {}
    cur_field = field
    value_columns = ('value ', 'value: ', 'amount ', 'value of the contract: ',)
    print lines
    for line in lines:
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



if __name__ == '__main__':
    samples = (
        ['Lowest offer 0,02 and highest offer 29 458,87 RON', 'Excluding VAT'],
        ['Value 686 986,81 EUR', 'Excluding VAT'],
        ['Value 1 850 000 EUR', 'Including VAT. VAT rate (%) 20.0'],
        ['Value 240 743,7 LTL', 'Including VAT. VAT rate (%) 5'],
        ['Lowest offer 550 000 and highest offer 700 000 EUR', 'Excluding VAT'],
        ['Value: 1 342 685,90 PLN', 'Including VAT. VAT rate (%) 23'],
        ['Value 732 758,62 EUR'],
        ['Value 5 404 552,35 EUR', 'Excluding VAT'],
        ['Lowest offer 35 536,45 and highest offer 323 753,45 EUR', 'Including VAT. VAT rate (%) 19']
        )

    for sample in samples:
        data = _text_value('v', sample)
        #pprint(data)
