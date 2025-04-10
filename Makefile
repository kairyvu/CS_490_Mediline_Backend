.PHONY: install venv clean run schema db_update fake

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
	python -m flask db init
	python -m flask db migrate
	python -m flask db upgrade

fake:
	flask seed-db