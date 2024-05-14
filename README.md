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
This will create blank database (no exposed ports) and start the python server, listening on port `1337`. Mind your firewall!

To stop the back-end run:
```bash
$ docker-compose down
```

