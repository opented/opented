import logging

from opented.core import freezer
from opented.queries import list_years, list_countries


log = logging.getLogger(__name__)


def all_args():
    years = list_years()
    countries = list_countries()

    yield {}
    for year in years:
        yield {'year': year.get('year')}

    for country in countries:
        yield {
            'country': country.get('iso_country'),
            'country_': country.get('iso_country')
        }

    for year in years:
        for country in countries:
            yield {
                'country': country.get('iso_country'),
                'country_': country.get('iso_country'),
                'year': year.get('year')
            }


@freezer.register_generator
def contracts():
    for arg in all_args():
        log.info("Generating contracts: %r", arg)
        yield arg


@freezer.register_generator
def documents():
    for arg in all_args():
        log.info("Generating documents: %r", arg)
        yield arg
