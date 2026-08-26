build: clean
	uvx hatch build

publish: build
	uvx hatch publish

clean:
	rm -rf dist

version:
	uvx hatch version

.PHONY: build publish clean version
