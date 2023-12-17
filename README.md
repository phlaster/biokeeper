# BioKeeper's backend

## Internals:
* Docker container with PostgreSQL
* Docker container with Python server
* Several usefull scripts for managing researches

## Running backend
To raise the whole back-end run:
```bash
$ docker-compose build
$ docker-compose up
```
This will create blank database (port `5432`) and start the python server, listening on port `1337`. Mind your firewall!

To stop the back-end run:
```bash
$ docker-compose down
```

## Creating new research
To create research. while back-end is running, firstly activate the python virtual environment:
```bash
$ python -m venv venv # creating virtual environment
$ source venv/bin/activate # activating virtual environment
$ pip install -r python/requirements.txt # installing required packages
```
Then run:
```bash
$ python ./python/src/add_research.py 1 10 2023.12.17 2024.01.01
```
where cl args are (in order):
* research type as integer;
* how many QR codes to create;
* first day of research;
* last day of research.
This will populate the db with research files, increment global counters etc. This will also generate directory with QR pictures and `.csv` file with text representation of QR codes.

## Regenerating research files
If you lost or deleted files for particular research, run:
```bash
$ python ./python/src/regenerate_research_files.py 1 # research id
```
This will bring pictures and `.csv` file back.