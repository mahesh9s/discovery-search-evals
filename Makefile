.PHONY: setup eval failures chart test all

setup:
	python -m pip install -r requirements.txt

eval:
	python -m evals.run

failures:
	python -m evals.failures --system hybrid
	python -m evals.failures --system hybrid_pinned

chart:
	python -m evals.chart

test:
	python -m pytest -q

all: eval failures chart test
