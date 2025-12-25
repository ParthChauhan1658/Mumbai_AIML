.PHONY: install test run clean lint

install:
	pip install -r requirements.txt

test:
	pytest tests/

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 app tests
