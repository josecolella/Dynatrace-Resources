


clean:
	rm *.png
	rm -rf __pycache__

test:
	nosetests tests/tests.py