.PHONY: install venv clean

venv:
	python -m venv venv
	. venv/bin/activate

install: venv
	pip install --upgrade pip
	pip install -r requirements.txt

clean:
	rm -rf venv