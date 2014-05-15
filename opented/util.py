import os
import csv
from unicodecsv import writer
from cStringIO import StringIO

from flask import Markup
from slugify import slugify
from jinja2.filters import do_filesizeformat

from opented.core import app


def file_size(url):
    try:
        size = float(os.path.getsize(os.path.join(get_output_dir(), 'data', url)))
    except OSError:
        size = 0
    for x in ['bytes','KB','MB','GB','TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0


def data_link(pattern, **values):
    vf = {'type': 'documents'}
    for k, v in values.items():
        vf[k] = slugify(unicode(v))
    doc_url = pattern % vf
    doc_size = file_size(doc_url)
    vf['type'] = 'awards'
    aw_url = pattern % vf
    aw_size = file_size(aw_url)
    return Markup('<a href="/data/'+doc_url+'">All documents</a> (CSV, '+doc_size+') &middot; <a href="/data/'+aw_url+'">Contract awards</a> (CSV, '+aw_size+')')


def csv_write_line(line):
    sio = StringIO()
    w = writer(sio, encoding='utf-8', quoting=csv.QUOTE_ALL)
    w.writerow(line)
    return sio.getvalue()


def stream_csv(q):
    keys = None
    for row in q:
        if keys is None:
            keys = row.keys()
            yield csv_write_line(keys)
        values = [row.get(k) for k in keys]
        yield csv_write_line(values)


@app.context_processor
def set_template_globals():
    return {
        'data': data_link
        }


def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))


@app.template_filter('format_num')
def format_num(num):
    if num is None or (isinstance(num, basestring) and not len(num)):
        return '-'
    try:
        return group(int(num))
    except Exception, e:
        raise
        return '-'


def get_output_dir():
    return 'site/'
