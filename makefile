# Makefile for installing dependencies and running the project

install: install-back install-front


install-back:
	cd back && uv sync

install-front:
	cd front && npm install


run-back:
	cd back && uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000

run-front:
	cd front && npm run dev
