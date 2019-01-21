.PHONY: develop teardown env launch-app clean

VENV_DIR = .venv
WITH_VENV = source $(VENV_DIR)/bin/activate


launch-app: env-exist
	$(WITH_VENV) && python run.py

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

clean:
	find . |  grep -E "(__pycache__|\.pyc$\)" | xargs rm -rf
	rm -rf *.egg-info/
	rm -rf *.pyc
