import dataset
import csv
import os

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

def run_metrics(row, columns):

    increment_total(row['country'])
    
    for column in columns:
        if column == 'year':
            add_to_country(row['country'], column, check_year(row[column]))
        else:
            add_to_country(row['country'], column, completeness(row[column]))

if __name__ == '__main__':

    metrics = {}

    if "DATABASE" in os.environ:
        db_addr = os.environ['DATABASE']
    else:
        db_addr = 'postgresql://localhost/opented'

    db = dataset.connect(db_addr) 

    results = csv.writer(open('results.csv', 'w'))
    results_percentage = csv.writer(open('results_percentage.csv', 'w'))

    columns = db['document'].columns
    columns = sorted(list(columns))

    for doc in db['document']:
        run_metrics(doc, columns)         

    headers = ['Country', 'Total Records']
    headers.extend(columns)
    
    results.writerow(headers)
    results_percentage.writerow(headers)

    for country in sorted(metrics.keys()):
        vals = [country, metrics[country]['total']]
        pct_vals = [country, metrics[country]['total']]
        for field in columns:
            vals.append(metrics.get(country).get(field, 0)) 
            pct_vals.append("{0:.2f}".format((metrics.get(country).get(field, 0)) / float(metrics[country]['total']) * 100)) 

        results.writerow(vals)
        results_percentage.writerow(pct_vals)



