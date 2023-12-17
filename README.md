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

# Managing requests
Each `research` consists of number of QR-codes. Front-end is expected to make GET requests after scanning QR-codes.

There're 2 types of valid request paths:
1. Short type -- checking, if QR-code exists in database:
    ```sh
    http://x.x.x.x:1337/req/$qrcode/
    # example: http://127.0.0.1:1337/req/abcdefghijklmnop/
    ```
    Where:

    * `qrcode`: 16 a-z lowercase chars.

    Possible response codes:
    * `202` -- Code is in database and is ready to use;
    * `406` -- Code has not being used, but the research is ended (alas!);
    * `410` -- The code has allready being used;
    * `422` -- No such code in database.

2. Long type -- attempt to push new sample into db:
    >
    ```bash
    http://x.x.x.x:1337/req/$qrcode/$temperature&$latitude,$longitude/
    # example: http://127.0.0.1:1337/req/abcdefghijklmnop/-5&51.523722,-0.158464/
    ```
    Where:

    * `qrcode`: 16 a-z lowercase chars;
    * `temperature`: integer value;
    * `latitude` and `longitude`: both floats separated with comma (`,`).

    Possible response codes:
    * `200` -- The QR-code was valid, the sample has being pushed, the code has became `used`;
    * `406` -- Code has not being used, but the research is ended;
    * `410` -- The code has allready being used;
    * `422` -- No such code in database.

Other response codes:
* `206` -- Unused QR code, followed by incorrect or incomplete request;
* `415` -- Request path starts with `/req/`, but the rest is incomprehensible;
* `410` -- The code has allready being used;
* `412` -- Totally incomprehensible request;
* `500` -- Internal Server Error (thrown if any database operation failed).