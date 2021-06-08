# https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css
#
deps/github.css:
	curl "https://gist.githubusercontent.com/dashed/6714393/raw/ae966d9d0806eb1e24462d88082a0264438adc50/github-pandoc.css" > "$@"

build/%.md: tests/%.py
	cells fmt "$<" > "$@"

build/%.html: build/%.md deps/github.css
	pandoc -s "$<" --css=deps/github.css -o "$@"

# EOF
