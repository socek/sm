venv := ./venv_sm
py := ./$(venv)/bin/python
pytest := ./$(venv)/bin/py.test
setup := flags/setup.py
database := src/sm.sqlite
devel.ini := src/development.ini
initialize_db := ./$(venv)/bin/initialize_sm_db

server: $(database)
	@pserve $(devel.ini)

$(database): $(setup)
	@$(initialize_db) $(devel.ini)

develop: $(setup)

flags:
	@mkdir flags

$(venv):
	@virtualenv --no-site-packages $(venv)

$(setup): flags $(venv) setup.py
	@$(py) setup.py develop
	@touch $@

test: $(setup)
	@py.test --tb=native src

cov: $(setup)
	@py.test --tb=native --cov-report html --cov-config pytest.ini src


