# BioKeeper's backend

## Internals:
* Docker container with PostgreSQL
* Docker container with Python server

## Setting up the environment:
This project shall be used with [**uv**](https://pypi.org/project/uv/) package installer.

**uv** installation:
```sh
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip.
pip install uv

# With pipx.
pipx install uv

# With Homebrew.
brew install uv

# With Pacman.
pacman -S uv
```
Creating **uv** venv:
```sh
uv venv  # Create a virtual environment at .venv.
```

Activating venv:
```sh
# On macOS and Linux.
source .venv/bin/activate

# On Windows.
.venv\Scripts\activate
```

Sync packages:
```sh
uv pip sync requirements.txt  # Install from a requirements.txt file.
```
You also need to install `docker` and `docker-compose`. Do so acording to your [OS-specific instructions](https://docs.docker.com/manuals/) and don't forget to add yourself to the `docker` group:
```sh
sudo groupadd docker
sudo usermod -aG docker $USER
```

## Testing
`postgres_db` container is instructed to put all the db-related data in the `postgres/data` directory, which has to be manually purged before running postgres after any changes to db schema. Following command can be used (requires `sudo`):
```sh
docker-compose down && sudo rm -rf postgres/data && docker-compose up db_postgres 
```
This will stop any running containers and remove the `postgres/data` directory before starting the `postgres_db` container again. To connect to db with any chosen frontend use:
```
host: 172.25.0.10
port: 5432
user: postgres
database: postgres
password: root
```
We used `cweijan.vscode-database-client2` VSCode extension and `DBeaver` GUI app.

After db is up and running, you can run tests with (don't forget to enable venv):
```sh
python python/test/DBManager_tests.py  
```
which takes around 20s.

Detailed logs can be found in `DBManager_tests.log` file.


