VIRTUAL_ENV_PATH=venv
SKIP_VENV="${NO_VENV}"
PYPI_API_KEY :=
PYPI_REPOSITORY_URL :=
ALPHA_VERSION :=

.DEFAULT_GOAL := pre_commit

pre_commit: copyright flake8

copyright:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Applying copyright..."; \
       ./development/copyright-update; \
       echo "DONE: copyright"; \
    )

flake8:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Runing Flake8 checks..."; \
       flake8 ./src/prana_rc --count --statistics; \
       echo "DONE: Flake8"; \
    )

build: copyright format flake8 clean
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Building wheel package..."; \
       bash -c "cd src && VERSION_OVERRIDE="$(ALPHA_VERSION)" python ./setup.py bdist_wheel --dist-dir=../dist --bdist-dir=../../build"; \
       echo "DONE: wheel package"; \
    )
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Building source distribution..."; \
       bash -c "cd src && VERSION_OVERRIDE="$(ALPHA_VERSION)" python ./setup.py sdist --dist-dir=../dist"; \
       echo "DONE: source distribution"; \
    )
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Building client wheel package..."; \
       bash -c "cd src && VERSION_OVERRIDE="$(ALPHA_VERSION)" python ./client_setup.py bdist_wheel --dist-dir=../dist --bdist-dir=../../build"; \
       echo "DONE: wheel client package"; \
    )

clean:
	@(rm -rf src/build dist/* *.egg-info src/*.egg-info .pytest_cache)

format:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Runing Black code formater..."; \
       black ./src/prana_rc; \
       echo "DONE: Black"; \
    )

publish:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       if [ ! -z $(PYPI_API_KEY) ]; then export TWINE_USERNAME="__token__"; export TWINE_PASSWORD="$(PYPI_API_KEY)"; fi; \
       if [ ! -z $(PYPI_REPOSITORY_URL) ]; then  export TWINE_REPOSITORY_URL="$(PYPI_REPOSITORY_URL)"; fi; \
       echo "Uploading to PyPi"; \
       twine upload -r pypi dist/*; \
       echo "DONE: Publish"; \
    )