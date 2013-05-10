from common import get_engine, get_output_dir
from dataset import freeze
import os
import sqlalchemy.sql.expression as sql

engine = get_engine()
document = engine['document'].table.alias('document')
cpv = engine['document_cpv'].table.alias('cpv')
awards = engine['awards'].table.alias('awards')

def documents_query():
    fo = document.join(cpv, document.c.uri==cpv.c.document_uri)
    cpvs = sql.func.array_to_string(sql.func.array_agg(cpv.c.code), ';').label('document_cpvs')
    q = sql.select([document, cpvs], from_obj=fo, use_labels=True)
    q = q.group_by(*list(document.columns))
    return q

def awards_query():
    fo = awards.join(document, document.c.uri==awards.c.uri)
    fo = fo.join(cpv, document.c.uri==cpv.c.document_uri)
    cpvs = sql.func.array_to_string(sql.func.array_agg(cpv.c.code), ';').label('document_cpvs')
    q = sql.select([awards, document, cpvs], from_obj=fo, use_labels=True)
    q = q.group_by(*list(awards.columns) + list(document.columns))
    return q

def store_csv(q, filename):
    q = engine.query(q)
    prefix = os.path.join(get_output_dir(), 'data')
    freeze(q, filename=filename, prefix=prefix)

if __name__ == '__main__':
    engine = get_engine()
    #print documents_query(engine, engine['document'].table.c.country=='DE')
    q = awards_query()
    q = q.where(document.c.country=='DE')
    store_csv(q, 'de.csv')
    print q
    engine.engine.execute(q)

