from common import as_document

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





