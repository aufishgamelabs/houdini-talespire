PYTHON ?= python3.14

.venv:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv .venv
	@echo "Activating virtual environment..."
	@. .venv/bin/activate

toolchain: .venv
	@echo "Building toolchain..."
	@$(PYTHON) -m pip install \
		black \
		isort \
		mypy \
		pylint \
		pytest 
		
