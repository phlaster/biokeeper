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



# Class structure

## DBManager
The DBManager class is the central class that manages the interactions with the database. It provides a set of common virtual methods that are shared across all managers.
- `generate_test_example(self, log=False) -> dict`
  - Create new `user`, `kit`, `research`, `sample` for testing purposes.
- `complete_weather_request(self, sample_id, log=False) -> None`
  - Tries to push weather data to **already collected** sample the database using `api.open-meteo.com`


### Common Virtual Methods
- `count(status: str = "all") -> int`
  - Returns the number of items with the specified status. If status is "all", it returns the total count.

- `has_status(status: str) -> tuple`
  - Checks if the given status is valid for the respective table (e.g., `user`, `kit`, `research`, or `sample`). Returns a tuple containing the `(status_id, description)` if valid, otherwise an empty tuple.

- `has(identifier, log=False) -> int`
  - Checks if an item with the given identifier (e.g., ID, name) exists. Returns the item's `id` if it exists, otherwise 0.

- `status_of(identifier, log=False) -> str`
  - Returns the `status_key` of the item with the given identifier. If the item does not exist, it returns `""`.

- `get_info(identifier, log=False) -> dict`
  - Returns a dictionary containing information about the item with the given identifier. If the item does not exist, returns `{}`.

- `get_all() -> dict`
  - Returns a dictionary containing information about all items of the respective table.

- `change_status(identifier, new_status: str, log=False) -> str`
  - Changes the `status` of the item with the given identifier. Returns the `new_status` if successful, or `""`.

## Managers

### KitsManager
- `new(n_qrs: int, log=False) -> int`
  - Creates a new kit with n_qrs QR codes. Returns the `kit_id` if successful, or `0`.

- `change_owner(kit_identifier, new_owner_identifier, log=False) -> int`
  - Changes the owner of the kit with the given identifier to the user with the specified `new_owner_identifier`. Returns the `kit_id` if successful, or `0`.

### UsersManager
- `new(user_name: str, password: str, log=False) -> int`
  - Creates a new user with the given user_name and password. Returns the `user_id` if successful, or `0`.

- `change_status(identifier, new_status: str, log=False) -> str`
  - Changes the status of the user with the given identifier to the specified new_status. Returns the `new_status` if successful, or `""`.

- `rename(user_identifier, new_user_name: str, log=False) -> str`
  - Renames the user with the given `user_identifier` to the specified `new_user_name`. Returns `new_user_name` if successful, or `""`.

- `change_user_password(identifier, new_password: str, log=False) -> int`
  - Changes the password of the user with the given identifier to the specified new_password. Returns `user_id` or `0`.

- `password_match(identifier, password: str, log=False) -> int`
  - Checks if the provided password matches the password of the user with the given identifier. Returns `user_id` or `0`.

### SamplesManager
- `new(qr_unique_hex: str, research_name: str, collected_at: datetime.datetime, gps: tuple[float, float], log=False) -> int`
  - Creates a new sample with the given parameters. Returns the `sample_id` or `0`.

- `push_weather(identifier, weather: str, log=False) -> int`
- `push_comment(identifier, comment: str, log=False) -> int`
- `push_photo(identifier, photo_bytes: bytes, log=False) -> int`
- `push_photo(identifier, photo_hex: str, log=False) -> int`
    - Returns `sample_id` or `0`

Extract from DB:
- `get_photo(identifier, log=False) -> bytes`
- `get_weather(identifier, log=False) -> str`


### ResearchesManager
- `new(research_name: str, user_name: str, day_start: datetime.date, research_comment: str = None, log=False) -> int`
  - Creates a new research with the given parameters. Returns `research_id` or `0`.

- `change_comment(identifier, comment: str, log=False) -> int`
  - Updates the comment for the research with the given `identifier`. Returns `research_id` or `0`.

- `change_day_end(identifier, day_end: datetime.date, log=False) -> int`
  - Updates the end date for the research with the given `identifier`. Returns `research_id` or `0`.