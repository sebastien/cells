from cells.kernel.python import PythonKernel

kernel = PythonKernel()
s = "session-0"
kernel.set(s, "a", [], "10", "python")
kernel.set(s, "b", [], "20", "python")
kernel.set(s, "c", ["a", "b"], "a * b", "python")
assert kernel.get(s, "a") == 10
assert kernel.get(s, "b") == 20
assert kernel.get(s, "c") == 10 * 20
kernel.set(s, "a", [], "20")
assert kernel.get(s, "a") == 20
assert kernel.get(s, "c") == 20 * 20
