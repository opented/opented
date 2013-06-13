import dataset
import csv
import os
from sqlalchemy.exc import ProgrammingError

""" 
    Script to process data quality metrics on TED procurement data
    @author = Kaitlin Devine
"""


def increment_total(country):
	if metrics.has_key(country):
		metrics[country]['total'] += 1
	else:
		metrics[country] = {'total': 1}

def add_to_country(country, field, success):
    if metrics[country].has_key(field):
        if success:
            metrics[country][field] += 1
    elif success:
        metrics[country][field] = 1

def completeness(val):
    if val and unicode(val).strip() != '':
        return True
    return False

def check_year(val):
    if int(val) > 2000:
        return True
    return False

def run_metrics(row, columns, country=None):
    if not country:
        country = row['country']

    increment_total(country)
    
    for column in columns:
        if column == 'year':
            add_to_country(country, column, check_year(row[column]))
        else:
            add_to_country(country, column, completeness(row[column]))

def write_out_results(file1, file2, headers):

    file1.writerow(headers)
    file2.writerow(headers)

    for country in sorted(metrics.keys()):
        vals = [country, metrics[country]['total']]
        pct_vals = [country, metrics[country]['total']]
        for field in columns:
            vals.append(metrics.get(country).get(field, 0)) 
            pct_vals.append("{0:.2f}".format((metrics.get(country).get(field, 0)) / float(metrics[country]['total']) * 100)) 

        file1.writerow(vals)
        file2.writerow(pct_vals)

if __name__ == '__main__':

    metrics = {}

    if "DATABASE" in os.environ:
        db_addr = os.environ['DATABASE']
    else:
        db_addr = 'postgresql://localhost/opented'

    db = dataset.connect(db_addr) 

     # create indexes on award and document for URI
    try:
        print "Checking for index on column uri in awards..."
        db.query('CREATE INDEX  awarduri on awards(uri)')
    except ProgrammingError:
        pass #already exists
    try:
        print "Checking for index on column uri in document..."
        db.query('CREATE INDEX docuri on documents(uri)')
    except ProgrammingError:
        pass #already exists

    # run awards through tests
    print "Running tests on awards table"
    columns = db['awards'].columns  
    award_headers = ['Country', 'Total Records']
    award_headers.extend(columns)
    awards = db.query('SELECT awards.*, country FROM awards LEFT JOIN document on document.uri=awards.uri')

    count = 0
    for aw in awards:
        #country = db['document'].find_one(uri=aw['uri'])['country']
        country = aw['country']
        run_metrics(aw, columns, country)
        count += 1
        if count % 100000 == 0: 
            print "count is %s" % count

    award_results = csv.writer(open('award_results.csv', 'w'))
    award_results_pct = csv.writer(open('award_results_pct.csv', 'w'))

    print "Writing out results"
    write_out_results(award_results, award_results_pct, award_headers)
    print "Done"

    # run documents through test
    print "Running tests on document table"
    metrics = {}

    doc_results = csv.writer(open('doc_results.csv', 'w'))
    doc_results_pct = csv.writer(open('doc_results_pct.csv', 'w'))

    columns = db['document'].columns
    columns = sorted(list(columns))

    count = 0
    for doc in db['document']:
        run_metrics(doc, columns)         
        count += 1
        if count % 100000 == 0: 
            print "count is %s" % count

    doc_headers = ['Country', 'Total Records']
    doc_headers.extend(columns)
    print "Writing out results"
    write_out_results(doc_results, doc_results_pct, doc_headers)
    print "Done"

    #Generating other misc stats
    misc_results = csv.writer(open('misc_results.csv', 'w'))
    
    for a in db.query("SELECT COUNT(DISTINCT(uri)) FROM awards;"):
        award_uris = a['count']

    for d in db.query("SELECT COUNT(DISTINCT(uri)) FROM document;"):
        doc_uris = d['count']

    print "There are %s distinct URIs in awards and %s distinct URIs in documents" % (award_uris, doc_uris)

    mismatch = db.query("SELECT country, year, count(*) FROM document WHERE uri NOT IN (SELECT awards.uri from awards WHERE awards.uri=uri) GROUP BY country, year ORDER BY country, year")
    misc_results.writerow(("Number of URIs that exist in document table but not awards table, grouped by country and year",))
    misc_results.writerow(("Country", "Year", "Number Missing"))
    for m in mismatch:
        misc_results.writerow((m['country'], m['year'], m['count']))

    # more info on top level stats?

