#
#   Package Management
#
.PHONY: cli_install install upgrade_dependencies

install:
	pip install -r requirements.txt

dev_install: install
	pip install -r dev_requirements.txt
	pre-commit install
	pre-commit install --hook-type commit-msg

upgrade_dependencies: dev_install
	pip install pip-tools
	pip-compile --upgrade --output-file ./requirements.txt requirements.in
	pip-compile --upgrade --output-file ./dev_requirements.txt dev_requirements.in


#
#   Extended Reports
#
.PHONY: mypy coverage

mypy:
	python -m mypy --config-file ./mypy.ini giges --txt-report .mypy_reports
	cat .mypy_reports/index.txt

coverage:
	pytest --alembic-folder=alembic --cov=pxsearch --cov-report term --cov-report html:reports/coverage-integration --cov-report term:skip-covered


#
#   Code Checks
#
.PHONY: pre-commit check semgrep

pre-commit:
	pre-commit run -a

check: pre-commit coverage

semgrep:
	semgrep --config=p/r2c-ci --config=p/flask

check-extended: check semgrep
#
#   Code Checks auto-fix
#
.PHONY: black

black:
	python -m black -l79 -tpy38 alembic pxsearch tests *.py
