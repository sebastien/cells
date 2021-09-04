# -- ASSIGNMENTS
value = [1, 2, 3, 4]
# -- NESTED_ASSIGNMENT


def f():
    value = [1, 2, 3, 4]
# -- FUNCTION_DEFINITION


def f(a, b, c, d):
    pass


# -- REFERENCES
# This is one anonymous scope:
# inputs: a, b
a + b


# This is one named scope, f:
# inputs: a, b, arg1
def f():
    a + b + arg1


# This is one named scope, g:
# inputs: f,a,b,do_something_there,one,two
def g(arg0, arg1, arg=2+a+b):
    f(a + b)
    if True:
        do_something_there(one, two)

# -- CLASS


class A:
    STATIC = 1

    def method(self, a, b, c):
        # Self reference
        return A.STATIC


# EOF
