# Makefile for installing dependencies and running the project

# Install dependencies for both back and front
install: install-back install-front

# Run both back and front
run: install run-back run-front


install-back:
ifeq ($(OS),Windows_NT)
	@if not exist back\.venv (python -m venv back\.venv)
	@back\.venv\Scripts\python -m pip install --upgrade pip
	@back\.venv\Scripts\python -m pip install -r back\requirements.txt
else
	@test -d back/.venv || python3 -m venv back/.venv
	@back/.venv/bin/python -m pip install --upgrade pip
	@back/.venv/bin/python -m pip install -r back/requirements.txt
endif


install-front:
	@cd front && npm install


run-back:
ifeq ($(OS),Windows_NT)
	@cmd /c start "back" powershell.exe -NoExit -Command "cd back; .\\.venv\\Scripts\\python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000"
else
	@sh -c 'cd back && ./.venv/bin/python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000'
endif


run-front:
ifeq ($(OS),Windows_NT)
	@cmd /c start "front" powershell.exe -NoExit -Command "cd front; npm run dev"
else
	@sh -c 'cd front && npm run dev'
endif
