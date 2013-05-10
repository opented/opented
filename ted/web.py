from flask import Flask, render_template
from common import get_engine

app = Flask(__name__)
engine = get_engine()
document = engine['document']
awards = engine['awards']

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


@app.route("/")
def index():
    years = document.distinct('year')
    countries = document.distinct('country')
    return render_template('index.html',
            years=years, countries=countries)

if __name__ == "__main__":
    app.run()



