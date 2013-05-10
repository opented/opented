from flask import Flask, Markup, render_template
from dataset.util import slug
from common import get_engine, list_years, list_countries

app = Flask(__name__)
engine = get_engine()
document = engine['document']
awards = engine['awards']

def data_link(pattern, **values):
    vf = {'type': 'documents'}
    for k, v in values.items():
        vf[k] = slug(unicode(v))
    doc_url = pattern % vf
    vf['type'] = 'awards'
    aw_url = pattern % vf
    return Markup('<a href="/data/'+doc_url+'">All documents</a> &middot; <a href="/data/'+aw_url+'">Contract awards</a> (CSV)')

@app.context_processor
def set_template_globals():
    return {
        'data': data_link
        }

# Permuations to export: 
#
# * All documents
# * All contracts
# * All documents by year
# * All contracts by year 
# * All documents by year and country
# * All contracts by year and country
# * All contracts by year and authority
# * All contracts by year and authority
# * All contracts by year and top-level CPV
# * All contracts by year and top-level CPV

@app.route("/country/<code>.html")
def country(code):
    return render_template('country.html',
            years=list_years())

@app.route("/index.html")
def index():
    return render_template('index.html',
            years=list_years(), countries=list_countries())

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()



