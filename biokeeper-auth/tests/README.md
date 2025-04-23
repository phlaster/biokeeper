# Instructions for running tests

**cd to biokeeper_auth**

**Create virtualenv:**
```sh
uv venv .venv_test
```

**Activate virtualenv:**
```sh
source .venv_test/bin/activate
```

**Install requirements for test:**
```sh
pip install -r requirements_test.txt
```

**Run test:**
```sh
cd biokeeper
docker compose -f docker-compose-tests.yaml down && docker compose -f docker-compose-tests.yaml up
```