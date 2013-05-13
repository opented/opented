
fetch:
	python ted/scraper.py

parse:
	dropdb opented
	createdb -E utf-8 opented
	python ted/parser.py

transform:
	psql -f transform.sql opented

freeze:
	rm -rf site/*
	mkdir -p site/data
	cp -R ted/static site
	pg_dump -f site/data/opented-latest.sql -c -O --inserts opented
	python ted/dump.py
	python ted/freeze.py

upload:
	s3cmd sync -c s3cmd.config --acl-public --guess-mime-type site/* s3://opented.pudo.org

all: fetch parse freeze upload

