
Features:
- FMT integration: automatically normalize/format a cell
- Lint integration: report errors and warnings with a cell
- Parsource integration for dependencies identification
- Inverted representation, ie. embedded in a language
- Kernels should identify their type, useful for mounting

Kernels:
- Go
- Bash
- File
- XML
- JSON
- CSV


Documentation:
- Using cells to write inline tests
- Micah Lerner has a great typo https://www.micahlerner.com, which is actually from Tufte!

Questions:
- Without a deamon, a session would be persisted in ~/.cells/sessions/HASH.json
- With a deamon, a session would be kept in memory, with the supporting kernels active

Ideas:
- For Python, the cell value is going to be latest locally assigned value,
  or the value from the locals with the cells name.
