
import sqlalchemy.sql.expression as sql
from sqlalchemy.sql import and_
from monnet.ted.util import engine, documents_table, contracts_table, cpvs_table


documents = documents_table.table.alias('document')
cpvs = cpvs_table.table.alias('cpv')
contracts = contracts_table.table.alias('awards')


def filter_by(year, country):
    filters = []
    if year is not None:
        filters.append(documents.c.year==str(year))
    if country is not None:
        filters.append(documents.c.iso_country==country.upper())
    return and_(*filters)


def documents_query(year=None, country=None):
    fo = documents.join(cpvs, documents.c.doc_no==cpvs.c.doc_no)
    cpvs_ = sql.func.array_to_string(sql.func.array_agg(cpvs.c.code), ';').label('document_cpvs')
    filters = filter_by(year, country)
    q = sql.select([documents, cpvs_], filters, from_obj=fo, use_labels=True)
    q = q.group_by(*list(documents.columns))
    return engine.query(q)


def contracts_query(year=None, country=None):
    fo = contracts.join(documents, documents.c.doc_no==contracts.c.doc_no)
    fo = fo.join(cpvs, documents.c.doc_no==cpvs.c.doc_no)
    cpvs_ = sql.func.array_to_string(sql.func.array_agg(cpvs.c.code), ';').label('document_cpvs')
    filters = filter_by(year, country)
    q = sql.select([contracts, documents, cpvs_], filters, from_obj=fo, use_labels=True)
    q = q.group_by(*list(contracts.columns) + list(documents.columns))
    return engine.query(q)


def list_years(year=None, country=None):
    cnt = sql.func.count(documents.c.id).label('documents')
    filters = filter_by(year, country)
    q = sql.select([documents.c.year, cnt], filters, from_obj=documents)
    q = q.group_by(documents.c.year)
    return list(engine.query(q))


def list_countries(year=None, country=None):
    cnt = sql.func.count(documents.c.id).label('documents')
    fld = sql.func.lower(documents.c.iso_country).label('iso_country')
    filters = filter_by(year, country)
    q = sql.select([fld, documents.c.country_common, cnt], filters, from_obj=documents)
    q = q.group_by(fld, documents.c.country_common)
    return list(engine.query(q))


def list_full(): #year=None, country=None):
    cnt = sql.func.count(documents.c.id).label('documents')
    fld = sql.func.lower(documents.c.iso_country).label('iso_country')
    #filters = filter_by(year, country)
    q = sql.select([fld, documents.c.country_common, documents.c.year, cnt],
                   from_obj=documents)
    q = q.group_by(fld, documents.c.country_common, documents.c.year)
    return list(engine.query(q))
