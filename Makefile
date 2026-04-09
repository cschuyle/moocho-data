ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

.PHONY: test
test:
	cd $(ROOT) && $(PYTHON) -m unittest discover -s test -p 'test_*.py' -v
