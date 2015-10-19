default:
	@htmlpp render main.pre.html

codegen:
	for i in `find . -name "*.pre.html"`; do htmlpp codegen $$i > $$i.py; done

clean:
	rm *.py
	rm **/*.py

.PHONY: default codegen clean
