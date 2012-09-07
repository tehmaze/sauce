build: .FORCE
	python setup.py build

install: .FORCE
	python setup.py install

pep8: .FORCE
	pep8 --ignore=E221,E241 sauce/

.FORCE:
