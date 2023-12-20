all:
	poetry install

test:
	poetry run pytest
