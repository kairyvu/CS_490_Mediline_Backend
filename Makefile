.PHONY: install venv clean run schema fake

venv:
	python -m venv venv
	. venv/bin/activate

install: venv
	pip install --upgrade pip
	pip install -r requirements.txt

clean:
	rm -rf venv
	rm -rf migrations

run:
	flask run

schema:
	rm -rf migrations
	./create_db.sh
	python -m flask db init
	python -m flask db migrate
	python -m flask db upgrade

upgrade_models:
	./create_db.sh

fake:
	flask seed-db