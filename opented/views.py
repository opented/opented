import os
from datetime import datetime

from flask import render_template, Response, url_for
from monnet.util import engine

from opented.core import app
from opented.queries import list_years, list_countries, list_full
from opented.queries import documents_query, contracts_query
from opented.util import get_output_dir, stream_csv


@app.route("/data/ted-documents.csv")
@app.route("/data/ted-documents-<year>.csv")
@app.route("/data/<country>/ted-documents-<country_>.csv")
@app.route("/data/<country>/ted-documents-<country_>-<year>.csv")
def documents(year=None, country=None, country_=None):
    q = documents_query(year=year, country=country)
    return Response(stream_csv(q), mimetype='text/csv')


@app.route("/data/ted-contracts.csv")
@app.route("/data/ted-contracts-<year>.csv")
@app.route("/data/<country>/ted-contracts-<country_>.csv")
@app.route("/data/<country>/ted-contracts-<country_>-<year>.csv")
def contracts(year=None, country=None, country_=None):
    q = contracts_query(year=year, country=country)
    return Response(stream_csv(q), mimetype='text/csv')


@app.route("/")
@app.route("/index.html")
def index():
    countries = list_countries()
    all_ = {
        'iso_country': None,
        'country_common': 'All countries',
        'section': 'all',
        'documents': sum([c.get('documents') for c in countries])
    }
    tables = [all_] + [dict(c) for c in countries]
    full = list_full()
    for table in tables:
        cc = table['iso_country']
        if 'section' not in table:
            table['section'] = cc
        args = {'country': cc, 'country_': cc}
        table['rows'] = [{
            'documents': table.get('documents'),
            'year': 'All years',
            'documents_url': url_for('documents', **args),
            'contracts_url': url_for('contracts', **args),
        }]
        years = full if cc is not None else list_years()
        for year in years:
            if 'iso_country' in year and year['iso_country'] != cc:
                continue
            args['year'] = year.get('year')
            year.update({
                'documents_url': url_for('documents', **args),
                'contracts_url': url_for('contracts', **args)
                })
            table['rows'].append(dict(year))
    tables = sorted(tables, key=lambda t: t.get('documents'), reverse=True)

    last_update = datetime.utcnow().strftime('%d.%m.%Y')
    return render_template('index.html', tables=tables, last_update=last_update)
