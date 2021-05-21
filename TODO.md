
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


Questions:
- Without a deamon, a session would be persisted in ~/.cells/sessions/HASH.json
- With a deamon, a session would be kept in memory, with the supporting kernels active
