import re

DOUBLES = re.compile(r'\s{1,}', re.M)

def tags_newlines(els):
    for el in els:
        if el.tail is None:
            el.tail = ''
        el.tail = '\n' + el.tail

def extract_plain(engine, uri, doc):
    body = doc.find('.//div[@class="DocumentBody"]')
    tags_newlines(body.findall('.//span'))
    tags_newlines(body.findall('.//br'))
    tags_newlines(body.findall('.//p'))
    text = body.xpath('string()')
    text = DOUBLES.sub(' ', text)
    engine['plain'].upsert({'uri': uri, 'text': text}, ['uri'])

def ctext(el):
    result = []
    if el.text:
        result.append(el.text)
    for sel in el:
        if sel.tag in ["br"]:
            result.append(ctext(sel))
            result.append('\n')
        else:
            result.append(ctext(sel))
        if sel.tail:
            result.append(sel.tail)
    return "".join(result)
