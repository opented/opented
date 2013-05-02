

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
    engine['plain'].upsert({'uri': uri, 'text': text}, ['uri'])
    



