all: diagram/schema-diagram.png

# SADisplay currently doesn't work with poetry...
install:
	poetry lock --no-update
	poetry install


test:
	poetry run pytest criticalmaas/

diagram/schema-diagram.png: diagram/create-diagram.py
	poetry install --with schema-diagram
	poetry run python $^ $@
