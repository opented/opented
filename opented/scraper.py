#!/usr/bin/python
"""
Scraper module for the EU Tenders Electoric Daily website.

This module can be used from the command line directly.

Example:
    python scraper.py 414837-2012
"""

import argparse
import logging
import sys
import time
import urllib2

import mechanize


logger = logging.getLogger(__name__)


class TedScraper(object):
    """
    Scraper for the Tenders Electronic Daily.

    Example:
        scraper = TedScraper()
        print scraper.scrape('414837-2012', 0)
        print scraper.scrape('414837-2012', 1)
    """

    USER_AGENT = 'TedScraper/0.6'
    URL_FORMAT = 'http://ted.europa.eu/udl' \
            '?uri=TED:NOTICE:%s:TEXT:EN:HTML&tabId=%s'

    def __init__(self):
        """
        Create a new scraper.
        """
        self.browser = None

    def open(self, doc_id, tab_id=0, max_retry=10):
        """
        Open a document tab and return the Mechanize response.

        Example:
            response = scraper.open('414837-2012', 0)
            print response.geturl()
        """
        response = None
        sleep_exp = 1
        url = self._build_url(doc_id, tab_id)
        while response is None:
            try:
                self._ensure_init()
                logger.debug("Opening document %s tab %s", doc_id, tab_id)
                return self.browser.open(url)
            except urllib2.URLError, e:
                logger.debug("Connection failed: %s", e.message)
                pass
            sleep_time = 2^sleep_exp
            logger.debug("Waiting %d seconds before retry", sleep_time)
            time.sleep(sleep_time)
            sleep_exp =+ 1
            self.browser = None

    def scrape(self, doc_id, tab_id=0, max_retry=10):
        """
        Scrape a document tab and return the HTML body.

        Example:
            print scaper.scrape('414837-2012', 0)
        """
        response = self.open(doc_id, tab_id, max_retry)
        print response.get_data()

    def _build_url(self, doc_id, tab_id):
        return self.URL_FORMAT % (doc_id, tab_id)

    def _ensure_init(self):
        if self.browser is None:
            self.browser = mechanize.Browser()
            self.browser.set_handle_robots(False)
            self.browser.addheader = [('User-Agent', self.USER_AGENT)]

            logger.debug("Opening TED homepage")
            self.browser.open("http://www.ted.europa.eu/")

            logger.debug("Selecting English language")
            self.browser.follow_link(
                text="Supplement to the Official Journal of the European Union",
            )


def parse_args(args):
    parser = argparse.ArgumentParser(description='Dump a TED document tab')
    parser.add_argument('-d', '--debug', action='store_true',
            help='show debugging info')
    parser.add_argument('doc_id', metavar='DOC_ID',
            help='the document identifier, e.g.: "414837-2012"')
    parser.add_argument('tab_id', metavar='TAB_ID', type=int,
            choices=range(5), default=0, nargs='?',
            help='the tab index, default: 0')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s')
    args = parse_args(sys.argv[1:])
    if args.debug:
        logger.setLevel(logging.DEBUG)
    scraper = TedScraper()
    print scraper.scrape(args.doc_id, args.tab_id)
