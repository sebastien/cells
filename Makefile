# https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
# PANDOC_CSS=https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
PANDOC_CSS=https://cdn.rawgit.com/sindresorhus/github-markdown-css/gh-pages/github-markdown.css
PANDOC=pandoc
PYTHON=python
CELLS=cells
CURL=curl
SOURCES_CELLS:=$(shell egrep "(//|#) --" -r src | cut -d: -f1 | sort | uniq)
PRODUCT_CELLS=$(SOURCES_CELLS:src/%=build/%.json)
PRODUCT_ALL=$(PRODUCT_CELLS)

build: $(PRODUCT_ALL)

run:
	$(PYTHON) -m http.server

deps/github.css:
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CURL)  > "$@"

build/%.json: src/%
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CELLS) fmt -tjson -o "$@" "$<"

# EOF
