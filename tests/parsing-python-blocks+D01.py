# --
# This is a straightforward example of the blocks that are typically
# supported in a Python source files. The Cells parser should identify each
# region with no problem.

# == symbol a
a = 10

# == symbol _
"Hello, wolrd!"

# == symbol f


def f(): return 10

# == symbol c


class C:

    # == symbol C.A
    A = [1, 2, 3]

    # == symbol C.m
    def m(self):
        return 10

# EOF
