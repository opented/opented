from flask import Flask
app = Flask(__name__)


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
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()



