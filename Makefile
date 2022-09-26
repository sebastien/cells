# https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
# PANDOC_CSS=https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
PANDOC_CSS=https://cdn.rawgit.com/sindresorhus/github-markdown-css/gh-pages/github-markdown.css
PANDOC=pandoc
PYTHON=python
CELLS=cells
CURL=curl
SOURCES_PY=$(shell find src/py -name "*.py")
SOURCES_CELLS:=$(shell egrep "(//|#) --" -r src | cut -d: -f1 | sort | uniq)
PRODUCT_CELLS=$(SOURCES_CELLS:src/%=build/%.json)
PRODUCT_ALL=$(PRODUCT_CELLS)
PYTHONPATH+=$(realpath src/py):$(realpath .deps/src/retro/src/py)
DEPS_ALL=\
	 .deps/src/retro\
	 .deps/src/tree-sitter-python\
	 .deps/src/tree-sitter-javascript\
	 .deps/src/tree-sitter-go\
	 .deps/run/treesitter.dep\
	 .deps/run/pip.dep

export PYTHONPATH
build: $(PRODUCT_ALL)

deps: $(DEPS_ALL)
	#
# gist edit https://gist.github.com/9f94ee52e539e624a73cec1b8ce3fdae
run: $(DEPS_ALL)
	echo $(PYTHONPATH)
	find src/py -name "*.py" | entr $(PYTHON) -m cells.api.server

deps/github.css:
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CURL)  > "$@"

build/%.json: src/%
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CELLS) fmt -tjson -o "$@" "$<"

.deps/run/pip.dep:
	@if [ ! python -m pip --version &> /dev/null ] ; then
		if  [ python -m ensurepip ] ; then
			echo "ERR Could not install pip: python -m ensurepip"
			exit 1
		fi
	fi
	if python -m pip --version &> /dev/null; then
		mkdir -p "$(dir $@)"
		touch "$@"
	else
		echo "ERR Could not install pip: python -m ensurepip"
		exit 1
	fi

.deps/run/treesitter.dep:
	@if python -m pip &> /dev/null; then
		echo "OK"
	else
		python -m ensurepip
	fi
	if python -m pip install --user -U tree-sitter; then
	 	mkdir -p "$(dir $@)"
	 	touch $@
	else
	 	exit 1
	fi

.deps/src/retro:
	@mkdir -p "$(dir $@)"
	git clone git@github.com:sebastien/retro.git $@

.deps/src/tree-sitter-%:
	@mkdir -p "$(dir $@)"
	git clone https://github.com/tree-sitter/tree-sitter-$* "$@"

.PHONY: build deps run
.ONESHELL:
# EOF
