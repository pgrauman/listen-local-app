.PHONY: develop teardown env launch-app clean test flake8

VENV_DIR = .venv
WITH_VENV = source $(VENV_DIR)/bin/activate


launch-app: env-exist config.py
	$(WITH_VENV) && python application.py

env: requirements.txt
	test -d $(VENV_DIR) || virtualenv -p python3 $(VENV_DIR)
	$(VENV_DIR)/bin/pip3 install -r requirements.txt
	touch $(VENV_DIR)/bin/

env-exist:
	test -f $(VENV_DIR)/bin/activate || $(MAKE) develop

develop: env
	$(WITH_VENV) && python setup.py develop

teardown:
	rm -rf .venv/

flake8:
	$(WITH_VENV) && flake8 listen_local_app

test: 
	$(WITH_VENV) && pytest

clean:
	find . |  grep -E "(__pycache__|\.pyc$\)" | xargs rm -rf
	rm -rf *.egg-info/
	rm -rf *.pyc
	rm -rf .pytest_cache/

aws-eb-prep: clean config.py
	sed 's/debug = True/debug = False/' config.py > tmp.py && mv tmp.py config.py
	zip -r listen-local-app.zip requirements.txt application.py listen_local_app config.py .elasticbeanstalk
	sed 's/debug = False/debug = True/' config.py > tmp.py && mv tmp.py config.py
