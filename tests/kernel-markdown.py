from cells.kernel.markdown import MarkdownKernel
kernel = MarkdownKernel()
s = "session-0"
kernel.set(s, "s1", [], "# Section 1", "markdown")
kernel.set(s, "s1_1", [], "## Section 1.2", "markdown")
print(kernel.get(s, "s1"))
