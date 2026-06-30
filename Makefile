#!/usr/bin/env make -f
# -*- makefile -*-

SHELL = bash -e
export BASH_ENV := $(HOME)/.bash_env
img_hash = $(shell docker images -q luisalejandro/agoras:latest)
exec_on_docker = docker compose \
	-p agoras -f docker-compose.yml exec \
	--user agoras app

# Release configuration
VERSION_TYPE ?= patch
APP_NAME ?= Agoras

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with tox -e lint (Ruff, pydocstyle, bandit, Pyright)"
	@echo "format - format Python code with tox -e format (Ruff)"
	@echo "lint-and-format - format then lint all production source"
	@echo "test - run coverage tests with tox"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "build - build PyPI sdist/wheel packages for all namespace packages"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test clean-docs

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .tox/
	rm -rf .coverage
	rm -rf htmlcov/

clean-docs:
	rm -rf docs/_build

lint: start
	@$(exec_on_docker) tox -e lint

format: start
	@$(exec_on_docker) tox -e format

lint-and-format: start
	@$(exec_on_docker) tox -e format
	@$(exec_on_docker) tox -e lint

test: start
	@$(exec_on_docker) tox -e coverage

test-all: start
	@$(exec_on_docker) tox -e all

functional-test: start
	# @$(exec_on_docker) bash test.sh twitter
	# @$(exec_on_docker) bash test.sh facebook
	# @$(exec_on_docker) bash test.sh linkedin
	# @$(exec_on_docker) bash test.sh instagram
	@$(exec_on_docker) bash test.sh discord

coverage: start
	@$(exec_on_docker) tox -e coverage
	@$(BROWSER) htmlcov/index.html

docs:
	@$(exec_on_docker) make -C docs clean
	@$(exec_on_docker) make -C docs html
	@$(BROWSER) docs/_build/html/index.html

servedocs: docs start
	@$(exec_on_docker) watchmedo shell-command -p '*.rst' -c 'make -C docs html' -R -D .

dependencies:
	@:

build: start
	@$(exec_on_docker) bash -c '\
		set -e; \
		for pkg in common media core platforms cli; do \
			( cd packages/$$pkg && python3 -m build && twine check dist/* ); \
		done'

install: clean start
	@$(exec_on_docker) pip3 install .

console: start
	@$(exec_on_docker) bash

virtualenv: start
	@python3 -m venv --clear --copies ./virtualenv
	@./virtualenv/bin/python3 -m pip install --upgrade pip
	@./virtualenv/bin/python3 -m pip install --upgrade setuptools
	@./virtualenv/bin/python3 -m pip install --upgrade wheel
	@./virtualenv/bin/python3 -m pip install -r requirements-dev.txt
	@./virtualenv/bin/python3 -m pip install -e packages/common
	@./virtualenv/bin/python3 -m pip install -e packages/media
	@./virtualenv/bin/python3 -m pip install -e packages/core
	@./virtualenv/bin/python3 -m pip install -e packages/platforms
	@./virtualenv/bin/python3 -m pip install -e packages/cli

PROJECT_NAME ?= agoras
all_ps_hashes = $(shell docker ps -q)

image:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml build \
		--build-arg UID=$(shell id -u) \
		--build-arg GID=$(shell id -g)

start:
	@if [ -z "$(img_hash)" ]; then\
		make image;\
	fi
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml up \
		--remove-orphans --no-build --detach

stop:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml stop

down:
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--remove-orphans

destroy:
	@echo
	@echo "WARNING!!!"
	@echo "This will stop and delete all containers, images and volumes related to this project."
	@echo
	@read -p "Press ctrl+c to abort or enter to continue." -n 1 -r
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--rmi all --remove-orphans --volumes

cataplum:
	@echo
	@echo "WARNING!!!"
	@echo "This will stop and delete all containers, images and volumes present in your system."
	@echo
	@read -p "Press ctrl+c to abort or enter to continue." -n 1 -r
	@if [ -n "$(all_ps_hashes)" ]; then\
		docker kill $(shell docker ps -q);\
	fi
	@docker compose -p $(PROJECT_NAME) -f docker-compose.yml down \
		--rmi all --remove-orphans --volumes
	@docker system prune -a -f --volumes

release:
	@./scripts/release.sh $${VERSION_TYPE}

release-patch:
	@./scripts/release.sh patch $${APP_NAME}

release-minor:
	@./scripts/release.sh minor $${APP_NAME}

release-major:
	@./scripts/release.sh major $${APP_NAME}


release-preflight:
	@make image
	@make dependencies
	@make build
	@make format
	@make lint
	@make test

undo-release:
	@: "$${VERSION:?Set VERSION=x.y.z before running make undo-release}"
	@VERSION=$${VERSION} ./scripts/rollback.sh release

.PHONY: clean clean-pyc clean-build clean-test clean-docs \
	help lint format lint-and-format test test-all functional-test coverage \
	docs servedocs build dependencies install console virtualenv \
	image start stop down destroy cataplum \
	release release-patch release-minor release-major release-preflight undo-release
