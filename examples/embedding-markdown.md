It it possible to  embed cells directly in a Markdown document. In this
case, the *fenced blocks* will be interpreted as fences and the cell definition
will be extracted from the first line.

We define the cell `hello`

```python hello
"Hello"
```

Followed by the cell `world`

```python who
"World"
```

And then a resulting anonymous cell combining both values `< hello who`

```python < hello who
f"${hello}, ${who}!"
```
You can then use `cell run FILE.md` to evaluate the cells, or use the `--inplace`
option to append the result of the evaluation at the end.
