#
#   Package Management
#
.PHONY: cli_install install upgrade_dependencies

cli_install:
	pip install -e .

install:
	pip install -r requirements.txt

upgrade_dependencies:
	pip install pip-tools
	pip-compile --upgrade --output-file ./requirements.txt requirements.in


