.PHONY: test format lint coverage clean run
test:
	@pytest src

format:
	@black src
	@isort -rc --atomic src

lint:
	@# Ignore white space errors for now
	@flake8 --ignore=E501,W291,W503 src || true

coverage:
	@pytest --cov src
	@coverage html
	@echo "Code coverage report in htmlcov"

clean:
	@rm -rf .coverage htmlcov

run:
	@src/main.py --skip-tracking --simulate-replies