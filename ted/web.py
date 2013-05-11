import os
from flask import Flask, Markup, render_template
from jinja2.filters import do_filesizeformat
from dataset.util import slug
from common import get_engine, list_years, list_countries, get_output_dir

app = Flask(__name__)
engine = get_engine()
document = engine['document']
awards = engine['awards']


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
        vf[k] = slug(unicode(v))
    doc_url = pattern % vf
    doc_size = file_size(doc_url)
    vf['type'] = 'awards'
    aw_url = pattern % vf
    aw_size = file_size(aw_url)
    return Markup('<a href="/data/'+doc_url+'">All documents</a> (CSV, '+doc_size+') &middot; <a href="/data/'+aw_url+'">Contract awards</a> (CSV, '+aw_size+')')

@app.context_processor
def set_template_globals():
    return {
        'data': data_link
        }

@app.route("/country/<code>.html")
def country(code):
    return render_template('country.html',
            years=list_years(country=code),
            country=code)

@app.route("/index.html")
def index():
    return render_template('index.html',
            years=list_years(), countries=list_countries())

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()



