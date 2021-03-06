venv := ./venv_sm
py := ./$(venv)/bin/python
pytest := ./$(venv)/bin/py.test
setup := flags/setup.py
database := src/sm.sqlite
devel.ini := src/development.ini
initialize_db := ./$(venv)/bin/initialize_sm_db
pserve := ./$(venv)/bin/pserve

server: $(database)
	@$(pserve) $(devel.ini) --reload

$(database): $(setup)
	@echo "Initializing db..."
	@rm -f src/sm.sqlite
	@$(initialize_db) $(devel.ini)

develop: $(setup)

flags:
	@mkdir flags

$(venv):
	@virtualenv -p python3 --no-site-packages $(venv)

$(setup): flags $(venv) setup.py
	@$(py) setup.py develop
	@touch $@

test: $(setup)
	@$(pytest) --tb=native src

cov: $(setup)
	@$(pytest) --tb=native --cov-report html --cov-config pytest.ini src --cov sm


