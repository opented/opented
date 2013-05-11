# OpenTED

OpenTED is a project aiming to open up the [EU Tender Electronic Daily](http://www.ted.europa.eu/) archive.


## Requirements

* Python 2.7
* Dependencies from `requirements.txt`
* PostgreSQL
* s3cmd


## How to run

The tool has several stages. After installing the dependencies, you need to set up 
a (postgres) database:

    $ createdb -E utf-8 opented

Next, you can run the entire script using this command: 

    $ make 

Since this will take several days, you may more often want to run the different 
stages separately, e.g. download: 

    $ make fetch 

Or processing: 

    $ make parse transform

Finally, generating the output files and uploading them to S3: 

    $ make freeze upload 

For the final step to work, you first need to configure s3cmd like this: 

    $ s3cmd -c s3cmd.config --configure 


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
