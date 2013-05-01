from lxml import html
from pprint import pprint

LIST_FIELDS = {
        'Publication reference:': 'publication_reference',
        'Publication date of the procurement notice:': 'publication_date',
        'Date of publication of the contract notice:': 'publication_date',
        'Lot number and lot title:': 'lot_nr_title',
        'Number and title of the lot:': 'lot_nr_title',
        'Number and titles of the lots:': 'lot_nr_title',
        'Contract value:': 'contract_value',
        'Contract number and value:': 'contract_value',
        'Date of award of the contract:': 'award_date',
        'Date of contract award:': 'award_date',
        'Date of contract signature:': 'award_date',
        'Number of tenders received:': 'num_tenders_received',
        'Overall score of chosen tender:': 'score_chosen_tender',
        'Overall score of selected tender:': 'score_chosen_tender',
        'Total score of the selected tender:': 'score_chosen_tender',
        'Name and address of successful tenderer:': 'recipient',
        'Name and address of the successful tenderer:': 'recipient',
        'Name, address and nationality of successful tenderer:': 'recipient',
        'DAC code:': 'dac_code',
        'Duration of contract:': 'contract_duration',
        'Contracting authority:': 'contracting_authority',
        'Legal basis:': 'legal_basis',

        'NAME AND ADDRESS OF ECONOMIC OPERATOR IN FAVOUR OF WHOM A CONTRACT AWARD DECISION HAS BEEN TAKEN': 'recipient',
        'INFORMATION ON VALUE OF CONTRACT': 'contract_value',
        'TOTAL FINAL VALUE OF CONTRACT(S)': 'total_value',
        'Total final value of contract(s)': 'total_value',
        'NAME, ADDRESSES AND CONTACT POINT(S)': 'authority',
        'DESCRIPTION': 'description',
        'Description': 'description',
        'Common procurement vocabulary (CPV)': 'cpv_codes',
    }


def text_html(field, el):
    return {field: html.tostring(el)}

def text_plain(field, el):
    for br in el.findall('.//br'):
        br.text = '\n'
    text = el.text_content()
    return {field: text}

def text_addr(field, el):
    #addr = el.find('.//p[@class="addr"]')
    #assert addr, el
    name = plain = text_plain(field, el)[field]
    if '\n' in name:
        name, _ = name.split('\n', 1)
    return {field + '_name': name, field + '_addr': plain}

FIELD_HANDLERS = {
    'description': text_plain,
    'recipient': text_addr,
    'authority': text_addr
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
        #if k not in LIST_FIELDS:
        #    print [k]
        k = LIST_FIELDS.get(k, k)
        if not len(v):
            continue
        data.update(FIELD_HANDLERS.get(k, text_html)(k, v))
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
        pprint(data)
    else:
        for contract in contracts:
            contract.update(data)
            pprint(contract)

def extract_awards(uri, doc):
    pass
