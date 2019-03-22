
VIRTUALENV := build/virtualenv

.PHONY:run
run:
	FLASK_APP=classifier FLASK_ENV=development flask run

.PHONY:db
db:
	FLASK_APP=classifier FLASK_ENV=development flask init-db

$(VIRTUALENV)/.installed: requirements.txt
	@if [ -d $(VIRTUALENV) ]; then rm -rf $(VIRTUALENV); fi
	@mkdir -p $(VIRTUALENV)
	virtualenv --python python3 $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip3 install -r requirements.txt
	touch $@


.PHONY: virtualenv
virtualenv: $(VIRTUALENV)/.installed

.PHONY: all
all: db run
