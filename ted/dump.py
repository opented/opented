from common import get_engine, get_output_dir, list_countries
from dataset import freeze
import os
import sqlalchemy.sql.expression as sql

engine = get_engine()
document = engine['document'].table.alias('document')
cpv = engine['document_cpv'].table.alias('cpv')
awards = engine['awards'].table.alias('awards')

def documents_query():
    fo = document.join(cpv, document.c.uri==cpv.c.document_uri)
    year = sql.func.substr(document.c.publication_date, 7).label('year')
    cpvs = sql.func.array_to_string(sql.func.array_agg(cpv.c.code), ';').label('document_cpvs')
    q = sql.select([document, year, cpvs], from_obj=fo, use_labels=True)
    q = q.group_by(*list(document.columns))
    return q

def awards_query():
    fo = awards.join(document, document.c.uri==awards.c.uri)
    fo = fo.join(cpv, document.c.uri==cpv.c.document_uri)
    year = sql.func.substr(document.c.publication_date, 7).label('year')
    cpvs = sql.func.array_to_string(sql.func.array_agg(cpv.c.code), ';').label('document_cpvs')
    q = sql.select([awards, year, document, cpvs], from_obj=fo, use_labels=True)
    q = q.group_by(*list(awards.columns) + list(document.columns))
    return q

def store_csv(q, filename):
    q = engine.query(q)
    prefix = os.path.join(get_output_dir(), 'data')
    freeze(q, filename=filename, prefix=prefix)

def dump_all():
    #print 'Dumping public bodies ...'
    #q = engine['document'].distinct('authority_name', 'country', 'nuts_code', 'authority_type_name')
    #store_csv(q, 'public_bodies.csv')
    for filename in [
        'opented-%s.csv',
        '{{year}}/opented-%s-{{year}}.csv',
        '{{slug:document_country}}/opented-%s-{{slug:document_nuts_code}}.csv',
        '{{slug:document_country}}/{{year}}/opented-%s-{{slug:document_nuts_code}}-{{year}}.csv',
        '{{slug:document_country}}/opented-%s-{{slug:document_country}}.csv',
        '{{slug:document_country}}/{{year}}/opented-%s-{{slug:document_country}}-{{year}}.csv',
        ]:
        q = documents_query()
        print [filename % 'documents']
        store_csv(q, filename % 'documents')
        q = awards_query()
        print [filename % 'awards']
        store_csv(q, filename % 'awards')

if __name__ == '__main__':
    dump_all()
