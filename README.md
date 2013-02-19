# OpenTED

OpenTED is a project aiming to open up the [EU Tender Electronic Daily](http://www.ted.europa.eu/) archive.


## Requirements

* Python 2.7
* Dependencies from `requirements.txt`


## Components


### Scraper

The scraper is used to get TED document tabs as raw HTML.


#### Command line usage

	python opented/scraper.py [-d] DOC_ID [TAB_ID]

Example:

	python opented/scraper.py 414837-2012

See `python opented/scraper.py -h` for details.


## License

Copyright 2013 Joost Cassee / OpenTED

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
