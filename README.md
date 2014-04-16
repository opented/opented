# OpenTED

OpenTED is a project aiming to open up the [EU Tender Electronic Daily](http://www.ted.europa.eu/) archive for journalistic and analytical purposes.

The actual scraper for TED data is not contained in this package, but in [monnet](http://github.com/pudo/monnet), a package that is shared with the [OpenInterests.eu](http://openinterests.eu) project which uses the same data. 

To operate, this site will require that ``monnet`` is set up in the same virtual environment and a fully-extracted database of TED data is available (i.e. the output of running ``make ted`` in the ``monnet`` folder).
