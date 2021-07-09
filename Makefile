# https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
# PANDOC_CSS=https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
PANDOC_CSS=https://cdn.rawgit.com/sindresorhus/github-markdown-css/gh-pages/github-markdown.css
PANDOC=pandoc
PYTHON=python
CELLS=cells
CURL=curl

run:
	$(PYTHON) -m http.server

deps/github.css:
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CURL)  > "$@"

build/%.md: tests/%.py
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	$(CELLS) fmt -tmd "$<" > "$@"

build/%.html: build/%.md deps/github.css
	@if [ ! -d "$(dir $@)" ]; then mkdir -p "$(dir $@)" ; fi
	@echo '<!DOCTYPE html>' > "@"
	@echo \
	'<html><head><meta charset="UTF-8" />' \
	'<link rel="stylesheet" href="$(PANDOC_CSS)" type="text/css" />' \
	'<style>pre.sourceCode{background-color:#170021;color:#B8B8B8;} .sourceCode .kw {color:#FFFFFF;font-weight:bold;}'\
	'pre.sourceCode {background-color:#170021;color:#B8B8B8;font-size:14px;line-height:17px;}'\
	'.sourceCode .kw {color:#FFFFFF;font-weight:bold;}'\
	'.sourceCode .im {color:#2D89AD}'\
	'.sourceCode .kw {color:#FFFFFF;font-weight:bold;}'\
	'.sourceCode .cf {color:#FFFFFF;font-weight:bold;}'\
	'.sourceCode .st {color:#1F8AFC;background-color:#1A2A42}'\
	'.sourceCode .va {color:#F5C400}'\
	'.sourceCode .fu {color:#F5C400}'\
	'.sourceCode .bu {color:#F5C400}'\
	'.sourceCode .op {color:#FFFFFF}'\
	'.sourceCode .co {color:#2A93A1; background-color:#222B3B}'\
	'#cells-footer {padding:1.25em;text-align: center;font-size:11px;line-height:14px;}' \
	'</style>' \
	'</head><body><div class=markdown-body style="padding:4em;max-width:55em;">' >> $@
	@$(PANDOC) $< >> $@
	@echo '<footer id="cells-footer">' >> $@
	@echo '<p>Notebook rendered with <a href="https://github.com/sebastien/cells">Cells</a></p>' >> $@
	@echo '</footer>' >> $@
	@echo '</div></body><html>' >> $@

# EOF
