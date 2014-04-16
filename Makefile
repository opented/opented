.PHONY: build

all: build upload

build:
	python opented/manage.py freeze

upload:
	#aws s3 sync --cache-control 84600 --acl public-read --exclude 'static/.webassets-cache/*' --delete build/ s3://www.offenerhaushalt.de/
