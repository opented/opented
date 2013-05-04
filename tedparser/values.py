import re
from pprint import pprint

NUMRE = '(-|\s{0,5}|\d[\. \d]*(,\d{1,2})?)'
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
        ['Lowest offer 35 536,45 and highest offer 323 753,45 EUR', 'Including VAT. VAT rate (%) 19'],
        ['Lowest offer 293 818 and highest offer  EUR', 'Excluding VAT'],
        ['Lowest offer 1 993 260,69 and highest offer  PLN', 'Including VAT. VAT rate (%) 7.0'],
        ['Value 0,0439 EUR', 'Excluding VAT'],
        ['Value 260 841,985 EUR', 'Excluding VAT'],
        ['Lowest offer 5 619 851,28 and highest offer  EUR', 'Including VAT. VAT rate (%) 19.0'],
        ['Lowest offer  and highest offer 1 882 483 EUR', 'Excluding VAT'],
        ['Value rd. 447 000 EUR', 'Excluding VAT'],
        ['Value 50 000 000 - 2 000 000 000 HUF', 'Excluding VAT'],
        ['Lowest offer 348 583,99 and highest offer  PLN', 'Including VAT. VAT rate (%) 22.0'],
        ['Lowest offer  and highest offer 800 400 EUR', 'Including VAT. VAT rate (%) 16.0'],
        ['Value  EUR', 'Excluding VAT'],
        ['Value 200 000 000 - 300 000 000 HUF', 'Excluding VAT'],
        ['Value 4,352 EUR', 'Including VAT. VAT rate (%)'],
        ['Lowest offer  and highest offer 597 835,79 EUR'],
        ['Value Importo stimato a corpo quale corrispettivo della prestazione complessiva a base di gara: 284 370,13 EUR (diconsi duecentoottantaquattromilatrecentosettanta/13) inclusi IVA ed oneri di legge EUR'],
        ['Lowest offer  and highest offer 6 414 183,82 EUR', 'Excluding VAT'],
        ['Value 245 586 (36 Monate) EUR', 'Including VAT. VAT rate (%) 19'],
        ['Value 7 440 000 = lordo EUR'],
        ['Lowest offer  and highest offer 143 103,45 EUR', 'Excluding VAT'],
        ['Lowest offer 1 113 794,42 and highest offer  EUR', 'Including VAT. VAT rate (%) 19'],
        ['Value 3 021 Teuro EUR', 'Excluding VAT'],
        ['Lowest offer 220 000 and highest offer  EUR', 'Excluding VAT'],
        [u'Lowest offer 1 228 547,98 Euro j\xe4hrlich bei einer Vertragsdauer von 4 Jahren and highest offer  EUR'],
        ['Lowest offer 158 798,13 and highest offer  EUR', 'Excluding VAT'],
        ['Lowest offer  and highest offer 466 831,08 EUR', 'Excluding VAT'],
        ['Value 355,000 GBP', 'Excluding VAT'],
        ['Lowest offer 76 041,40 and highest offer  EUR', 'Including VAT. VAT rate (%) 19'],
        ['Lowest offer 74 215,86 and highest offer  EUR', 'Including VAT. VAT rate (%) 19'],
        ['Lowest offer 158 798,13 and highest offer  EUR', 'Excluding VAT'],
        ['Value 6 000 000 (BA I - III) EUR', 'Excluding VAT'],
        ['Lowest offer 237 405 and highest offer  EUR', 'Including VAT. VAT rate (%) 19'],
        ['Value 594 000 (importo lordo) EUR'],
        ['Lowest offer 573 400 and highest offer  EUR', 'Excluding VAT'],
        ['Value 500 000 - 700 000 EUR', 'Excluding VAT'],
        ['Lowest offer  and highest offer 105 000 000,00 CZK', 'Excluding VAT'],
        ['Lowest offer 20,02 and highest offer  EUR'],
        ['Lowest offer 319 000 and highest offer  EUR', 'Including VAT. VAT rate (%) 16'],
        ['Lowest offer 8 358 000 and highest offer  EUR', 'Excluding VAT'],
        ['Lowest offer 196 350,90 and highest offer  EUR', 'Including VAT. VAT rate (%) 19'],
        ['Lowest offer Cost per day after 60 Days: 1.10; One-Off Service Charge: 71.00; Inst. Rem & Maint cost to GMP(Normal Hours/Out of hours); 106.00/106.00; Average Cost per Force (Normal Hours/Out of Hours): 119.14/148.14 and highest offer Cost per day after 60 Days: 0.50; One-Off Service Charge: 950.00; Inst. Rem & Maint cost to GMP(Normal Hours/Out of hours): 950.00/1100.00; Average Cost per Force (Normal Hours/Out of Hours): 950.00/1100.00 GBP', 'Excluding VAT'],
        ['Lowest offer  and highest offer 8 000 000 EUR', 'Including VAT. VAT rate (%) 19'],
        ['Lowest offer 612 053 and highest offer  EUR', 'Excluding VAT']
        )

    for sample in samples:
        data = _text_value('v', sample)
        #pprint(data)
