
freeze:
	rm -rf site/*
	cp -R ted/static site
	python ted/dump.py
	python ted/freeze.py

all: freeze

