.PHONY: install dev test cov allure-results docker-build docker-run

install:
	python -m pip install -e .

dev:
	uvicorn app.main:app --reload

test:
	python -m pytest -q

cov:
	python -m pytest --cov=app --cov-report=term-missing --cov-report=html

allure-results:
	python -m pytest --alluredir=reports/allure-results

docker-build:
	docker build -t gameops-agent-test-platform .

docker-run:
	docker run -p 8000:8000 gameops-agent-test-platform
