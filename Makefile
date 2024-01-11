.PHONY: install lock test diagram publish

# Install dependencies
install:
	poetry install

# Lock dependencies to poetry.lock
lock:
	poetry lock --no-update

# Run tests
test:
	poetry run pytest criticalmaas/

# Create schema diagram
diagram: diagram/schema-diagram.png

diagram/schema-diagram.png: diagram/create-diagram.py
	poetry install --with schema-diagram
	poetry run python $^ $@

# Publish to PyPI, ensuring that the working directory is clear
publish:
	poetry lock --no-update
	poetry build
	git diff-index --quiet HEAD --
	poetry publish
	git tag -a v$(shell poetry version -s) -m "Version $(shell poetry version -s)"