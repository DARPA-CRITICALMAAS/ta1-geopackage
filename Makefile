all: diagram/schema-diagram.png

# SADisplay currently doesn't work with poetry...
install:
	poetry lock --no-update
	poetry install


test:
	poetry run pytest

diagram/schema-diagram.png: create-diagram.py
	poetry run python $^ $@
