# Auth Service

## Container with pre-installed uv
Build container with pre-installed uv using this command:
```sh
echo 'FROM python:3.11-slim-buster
RUN pip install uv' | docker build -t python:3.11-slim-buster-uv -
```

## Environment variables
This folder must contain two environment files: `.db.env` and `.rtoken.salt.env`.

Content format:

`biokeeper/biokeeper-auth/.db.env`
```sh
POSTGRES_USER=biokeeper_auth
POSTGRES_PASSWORD=YOUR_SECRET_PASSWORD
POSTGRES_DB=auth_db
```

`biokeeper/biokeeper-auth/.rtoken.salt.env`
```sh
REFRESH_TOKEN_HASH_SALT=YOUR_SECRET_SALT # random string with 32+ symbols
```