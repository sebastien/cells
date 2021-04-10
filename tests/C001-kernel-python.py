from cells.kernel.python import PythonKernel
# --
# The main goal here is ensure that we can create a standalone kernel and that the
# dataflow is working properly. In the following we do `C = A * B` and make sure the
# setting and getting of slots work.
# --
kernel = PythonKernel()
s = "session-0"
kernel.set(s, "a", [], "10", "python")
kernel.set(s, "b", [], "20", "python")
kernel.set(s, "c", ["a", "b"], "a * b", "python")
assert kernel.get(s, "a") == 10
assert kernel.get(s, "b") == 20
assert kernel.get(s, "c") == 10 * 20
# --
# Now we test the invalidation and the recalculation. We update the value for
# `A`, which then should update `C`
# --
kernel.invalidate(s, ["c"])
kernel.set(s, "a", [], "20")
assert kernel.get(s, "a") == 20
assert kernel.get(s, "c") == 20 * 20
