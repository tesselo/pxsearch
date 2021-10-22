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
#   Code Checks
#
.PHONY: pre-commit check coverage

pre-commit:
	pre-commit run -a

coverage:
	pytest --alembic-folder=alembic --cov=pxsearch --cov-report term --cov-report html:reports/coverage-integration --cov-report term:skip-covered


check: pre-commit coverage

#
#   Extended Reports
#
.PHONY: smells security complexity check-advanced check-extended

smells:
	semgrep --config=p/r2c-ci --config=p/flask

security:
	bandit -r pxsearch

complexity:
	wily build pxsearch
	wily report pxsearch

doc-style:
	pydocstyle pxsearch

check-advanced: smells security
check-picky: complexity doc-style
check-extended: check check-advanced check-picky

#
#   Code Checks auto-fix
#
.PHONY: black

black:
	python -m black -l79 -tpy38 alembic pxsearch tests *.py
