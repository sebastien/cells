# --
# This is a collection of the edge cases of the D01 version.

# Here we test the multiple assignment
# -- a,b,c,d
a, b, c, d = (10, 20, 30, 40)


# -- decorated
def decorated(cls):
    return cls


# -- T
T = int


# Here we test the decoration
# --  C
@decorated
class C:

    # Here we test the
    # -- C.A < T
    A: list[T] = [1, 2, 3]

    # -- C.m
    @classmethod
    def m(cls):
        return 10

# EOF
