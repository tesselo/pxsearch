#
#   Package Management
#
.PHONY: cli_install install upgrade_dependencies

install:
	poetry install --no-dev

dev_install:
	poetry install
	pre-commit install
	pre-commit install --hook-type commit-msg

upgrade_dependencies:
	poetry upgrade

#
#   Code Checks
#
.PHONY: pre-commit check coverage

pre-commit:
	pre-commit run -a

coverage:
	poetry run pytest --alembic-folder=alembic --cov=pxsearch --cov-report term --cov-report html:reports/coverage-integration --cov-report term:skip-covered


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
