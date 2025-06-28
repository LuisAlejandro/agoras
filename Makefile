#!/usr/bin/env make -f
# -*- makefile -*-

SHELL = bash -e
all_ps_hashes = $(shell docker ps -q)
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
	@echo "lint - check style with flake8"
	@echo "format - format Python code with autopep8"
	@echo "lint-and-format - lint and format all Python files"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test clean-docs

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

clean-docs:
	rm -fr docs/_build

lint: start
	@$(exec_on_docker) flake8 agoras

format: start
	@$(exec_on_docker) autopep8 --in-place --recursive --aggressive --aggressive agoras tests

lint-and-format: start
	@$(exec_on_docker) autopep8 --in-place --recursive --aggressive --aggressive agoras tests
	@$(exec_on_docker) flake8 agoras

test: start
	@$(exec_on_docker) python3 -m unittest -v -f

test-all: start
	@$(exec_on_docker) tox

functional-test: start
	# @$(exec_on_docker) bash test.sh twitter
	# @$(exec_on_docker) bash test.sh facebook
	# @$(exec_on_docker) bash test.sh linkedin
	# @$(exec_on_docker) bash test.sh instagram
	@$(exec_on_docker) bash test.sh discord

coverage: start
	@$(exec_on_docker) coverage run --source agoras -m unittest -v -f
	@$(exec_on_docker) coverage report -m
	@$(exec_on_docker) coverage html
	@$(BROWSER) htmlcov/index.html

docs:
	@$(exec_on_docker) make -C docs clean
	@$(exec_on_docker) make -C docs html
	@$(BROWSER) docs/_build/html/index.html

servedocs: docs start
	@$(exec_on_docker) watchmedo shell-command -p '*.rst' -c 'make -C docs html' -R -D .

release: clean start dist
	@twine upload dist/*

dist: clean start
	@$(exec_on_docker) python3 -m build
	@ls -l dist

install: clean start
	@$(exec_on_docker) pip3 install .

image:
	@docker compose -p agoras -f docker-compose.yml build \
		--build-arg UID=$(shell id -u) \
		--build-arg GID=$(shell id -g)

start:
	@if [ -z "$(img_hash)" ]; then\
		make image;\
	fi
	@docker compose -p agoras -f docker-compose.yml up \
		--remove-orphans --no-build --detach

console: start
	@$(exec_on_docker) bash

virtualenv: start
	@python3 -m venv --clear ./virtualenv
	@./virtualenv/bin/python3 -m pip install --upgrade pip
	@./virtualenv/bin/python3 -m pip install --upgrade setuptools
	@./virtualenv/bin/python3 -m pip install --upgrade wheel
	@./virtualenv/bin/python3 -m pip install -r requirements.txt -r requirements-dev.txt

stop:
	@docker compose -p agoras -f docker-compose.yml stop app

down:
	@docker compose -p agoras -f docker-compose.yml down \
		--remove-orphans

destroy:
	@echo
	@echo "WARNING!!!"
	@echo "This will stop and delete all containers, images and volumes related to this project."
	@echo
	@read -p "Press ctrl+c to abort or enter to continue." -n 1 -r
	@docker compose -p agoras -f docker-compose.yml down \
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
	@docker compose -p agoras -f docker-compose.yml down \
		--rmi all --remove-orphans --volumes
	@docker system prune -a -f --volumes

# Release management
release:
	@./scripts/release.sh $(VERSION_TYPE)

release-patch:
	@./scripts/release.sh patch $(APP_NAME)

release-minor:
	@./scripts/release.sh minor $(APP_NAME)

release-major:
	@./scripts/release.sh major $(APP_NAME)

# Hotfix management
hotfix:
	@./scripts/hotfix.sh $(APP_NAME)

.PHONY: clean-pyc clean-build docs clean release release-patch release-minor release-major hotfix
