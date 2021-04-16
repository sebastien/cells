```

           ,gggg,
         ,88"""Y8b,         ,dPYb, ,dPYb,
        d8"     `Y8         IP'`Yb IP'`Yb
       d8'   8b  d8         I8  8I I8  8I
      ,8I    "Y88P'         I8  8' I8  8'
      I8'           ,ggg,   I8 dP  I8 dP    ,g,
      d8           i8" "8i  I8dP   I8dP    ,8'8,
      Y8,          I8, ,8I  I8P    I8P    ,8'  Yb
      `Yba,,_____, `YbadP' ,d8b,_ ,d8b,_ ,8'_   8)
        `"Y8888888888P"Y8888P'"Y888P'"Y88P' "YY8P8P

```

Cells is a dataflow engine along with a set of tools that
support the creation of text-based polyglot notebooks
in a similar way as [Jupyter](https://jupyter.org/) or [Observable](https://observablehq.com/).

Like Observable, Cells uses a dataflow approach to *automatically recalculate* cells when their inputs have changed. Like Jupyter, Cells uses different kernels to support different languages and formats.

Here is an example:

```
-- hello:js
"Hello"
-- who:js
"World"
-- :js < hello who
`${hello}, ${who}!`
```

Running that document through `cells run` will result in:

```
== hello
	"Hello"
== world
	"World"
==
	"Hello, World!"
```

# Interactive session

You can also run interactive sessions using cells, that you can
update like so:

`cells run -s SESSION DOCUMENT.cd`

This will reuse any previously calculated cell result from the previous
session for any cell that has not changed.
