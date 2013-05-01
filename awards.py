from lxml import html
from pprint import pprint

def parse_mli(mli):
    key = None
    keys = mli.cssselect('span.timark')
    if len(keys):
        key = keys.pop().text
    text = mli.cssselect('.txtmark')
    if len(text):
        text = html.tostring(text.pop())
        text, chop = text.rsplit('<', 1)
        chop, text = text.split('>', 1)
        text = text.replace('<br>', '\n').strip()
    return key, len(text)

def parse_list(el):
    data = {}
    for mli in el.findall('./div[@class="mlioccur"]'):
        k, v = parse_mli(mli)
        data[k] = v
    return data

def parse_award(doc):
    body = doc.find('.//div[@class="DocumentBody"]')
    data = parse_list(body)
    title = None
    for seq in doc.cssselect('.DocumentBody > .grseq'):
        titles = seq.cssselect('.tigrseq')
        if len(titles):
            title = titles.pop().xpath('string()')
        subtitle = seq.find('./span')
        if subtitle is not None:
            subtitle = subtitle.text
        section = parse_list(seq)
        if subtitle:
            if title not in data:
                data[title] = {}
            data[title][subtitle] = section
        else:
            data[title] = section
    pprint(data)
