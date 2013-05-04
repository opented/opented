import re
from pprint import pprint

NUMRE = '(-|[\., \d]*(,\d{1,2})?)'
CURRE = '(HT )?(?P<cur>[A-Z]{3})\.?'

VALUE_LINE_RE = re.compile('^(Value|Amount|Value of the contract):?([^\d]*|.*- )?(?P<val>' + \
        NUMRE+')[^\d]*(\s*\(.*\)\s*)?'+CURRE, re.M)
PLAIN_VALUE_RE = re.compile('^(?P<val>'+NUMRE+') '+CURRE+'.*')
RANGE_LINE_RE = re.compile('^Lowest offer (?P<lo>'+NUMRE+').* (and )?highest ' + \
        'offer (?P<hi>(\-|'+NUMRE+')) '+CURRE)
VAT_LINE_RE = re.compile('^(Excluding VAT|Including VAT).*')
INI_LINE_RE = re.compile('^Initial estimated total value of the contract')
TOTAL_LINE_RE = re.compile('^Total final value of the contract')
TERMS_LINE_RE = re.compile('^(If annual or monthly value|Number of years|Number of months).*')
CONTRACT_LINE_RE = re.compile('^(Contract|CONTRACT|Service contract)')
IGNORE_LINE_RE = re.compile('(^Lot|^$)')


def to_number(value):
    if value is not None:
        value = value.replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return float(value)
        except Exception, ex: pass


def text_value(field, el):
    from awards_tab import text_plain
    plain = text_plain(field, el)[field]
    return _text_value(field, plain.split('\n'))

def _text_value(field, lines):
    cur_field = field
    data = {field+'_text': '\n'.join(lines)}

    def store_vat(f, m):
        data[f+'_vat'] = m.group(0)

    def store_value(f, m):
        data[f] = to_number(m.group('val'))
        data[f+'_currency'] = m.group('cur')

    def store_range(f, m):
        data[f+'_currency'] = m.group('cur')
        data[f+'_lowest'] = to_number(m.group('lo'))
        data[f+'_highest'] = to_number(m.group('hi'))
        data[f] = data[f+ '_lowest'] if data[f+'_lowest'] is not None \
            else data[f+'_highest']

    def set_initial(f, m):
        return field + '_initial'

    def set_total(f, m):
        return field

    def store_terms(f, m):
        data[f+'_terms'] = m.group(0)
        
    def store_contract(f, m):
        data['contract_id'] = m.group(0)

    def store_nop(f, m):
        pass

    handlers = {
        VAT_LINE_RE: store_vat,
        VALUE_LINE_RE: store_value,
        PLAIN_VALUE_RE: store_value,
        RANGE_LINE_RE: store_range,
        INI_LINE_RE: set_initial,
        TOTAL_LINE_RE: set_total,
        TERMS_LINE_RE: store_terms,
        CONTRACT_LINE_RE: store_contract,
        IGNORE_LINE_RE: store_nop
        }

    for line in lines:
        matched = False
        for regex, handle in handlers.items():
            m = regex.match(line)
            if m is not None:
                f = handle(cur_field, m)
                if f is not None:
                    cur_field = f
                matched = True
        if not matched: 
            #print 'XXX', lines
            print [line]
    
    #pprint(data)
    return data

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
