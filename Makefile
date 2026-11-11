.PHONY: install train evaluate test quality api ui build
install:
	python -m pip install -r requirements.txt -r requirements-dev.txt
train:
	ticket train
evaluate:
	ticket evaluate
	python src/mesurer.py
	python src/courbe_seuil.py
test:
	python -m pytest -q --cov=ticket_agent --cov=api --cov=ui.client --cov-report=term-missing
quality:
	python -m ruff check .
	python -m mypy ticket_agent api ui src scripts
api:
	ticket serve
ui:
	ticket ui
build:
	python -m build
