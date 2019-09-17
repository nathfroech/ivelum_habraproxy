.PHONY: virtualenv
virtualenv:
	@virtualenv -p python3.6 env

.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

.PHONY: env_file
env_file:
	@python helpers/generate_env_file.py

.PHONY: lint
lint:
	@pre-commit run --all-files

.PHONY: test
test:
	@pytest -c setup.cfg

.PHONY: coverage
coverage:
	@pytest -c setup.cfg --cov-config setup.cfg -s --cov-report term --cov habraproxy

.PHONY: runserver
runserver:
	FLASK_APP=habraproxy/app.py FLASK_ENV=development flask run
