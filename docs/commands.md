# Cells commmands

## High level interface

## `cells run [-S SESSION] FILE?`

Runs the given `FILE`, optionally storing the result as part of the given `SESSION`. When
a session is provided, consecutive runs will reuse previously computed values if the cells
have not changed.

When no `FILE` is given, then the input will be read from *stdin*.

If the `FILE` does not ends in `.cd`, the cells command will try to extract cell definitions
for the format (if it is a [known format](#)).

## `cells fmt FILE`

Formats the given FILE so that its syntax is normalized.

## Low level interface

## `cells eval [-S SESSION] [-t TYPE] COMMAND ARG=VALUE…`

Evaluates the given command, instanciating the corresponding kernel if necessary.

## Kernels

### `cells kernel [-p|--port 8000] LANG`

Starts a kernel for the given `LANG`uage, running it interactively in the foreground. The kernel
will be accessible through the given port and can be interacted with through the given JSONRPC
port.

### `cells kernel -m|--mount=URL`

Mounts the given kernel as a kernel available to the current user.

### `cells kernel -u|--unmount=URL`

Unmounts the given kernel

### `cells kernel -l|--list`

Lists the kernels currently available, the ones currently running will be prefixed with `*`

```
$ cells kernel -l
* python namedpipe:~/.cells/kernels/py
* javascript  namedpipe:~/.cells/kernels/js
  markdown
```

### `cells kernel -s|--shutdown [NAME…]`

Shuts down the given kernels (or all kernels if no name is given). The kernel(s)
will still be available, but will need to be restarted if not active.
