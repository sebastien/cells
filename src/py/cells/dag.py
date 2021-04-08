from typing import Generic, TypeVar, Dict, List, Iterable, OrderedDict, Optional

T = TypeVar("T")


class DAG(Generic[T]):
    """A simple data structure to defined a directed acyclic graph that can
    be traversed back and forth."""

    def __init__(self):
        self.nodes: Dict[str, Optional[T]] = {}
        self.outputs: Dict[str, List[str]] = {}
        self.inputs: Dict[str, List[str]] = {}

    def toPrimitive(self):
        return {
            "nodes": self.nodes,
            "edges": self.outputs,
        }

    def setNode(self, node: str, value: Optional[T] = None):
        """Associates a value to the node of the given name. Use this to map
        values to the DAG"""
        if node not in self.nodes:
            self.nodes[node] = value
            self.inputs[node] = []
            self.outputs[node] = []
        if value != None:
            self.nodes[node] = value
        return self

    def addInput(self, node: str, inputNode: str):
        """Add the given node as input to this node"""
        self.setNode(node)
        if inputNode not in self.nodes:
            self.setNode(inputNode)
        assert node in self.inputs, "Output node should have been registered before"
        assert inputNode in self.outputs, "Input node should have been registered before"
        self.inputs[node].append(inputNode)
        self.outputs[inputNode].append(node)
        # TODO: Detect cycle
        return self

    def addInputs(self, node: str, inputNodes: Iterable[str]):
        """Add the given node as inputs to this node"""
        for _ in inputNodes:
            self.addInput(node, _)
        return self

    def addOutput(self, node: str, outputNode: str):
        """Add the given node as outputs of this node"""
        return self.addInput(outputNode, node)

    def addOutputs(self, node: str, outputNode: Iterable[str]):
        """Add the given nodes as outputs of this node"""
        for _ in outputNode:
            self.addOutput(node, _)
        return self

    def descendants(self, node: str) -> Iterable[str]:
        """Iterates through the descendants of the given node"""
        children = self.outputs.get(node, ())
        # NOTE: If there is a cycle, we're fucked!
        for _ in children:
            yield _
        for _ in children:
            yield from self.descendants(_)

    def ranks(self) -> OrderedDict[str, int]:
        """Returns the rank for each node in the graph, as a mapping between the
        node id and the rank. Base rank is 0, result is sorted by ascending rank."""
        ranks: Dict[str, int] = dict((k, 0) for k in self.nodes)
        while True:
            has_changed = False
            for node in self.nodes:
                rank = max(ranks[_] for _ in self.inputs[node]) + \
                    1 if self.inputs[node] else 0
                has_changed = has_changed or rank != ranks[node]
                ranks[node] = rank
            if not has_changed:
                break
        return OrderedDict((k, v) for k, v in sorted(ranks.items(), key=lambda _: _[1]))

    def successors(self) -> OrderedDict[str, List[str]]:
        # NOTE: This may return a N * N-1 matrix, with N the number of nodes,
        # so this might take up a bit of memory on large graphs.
        node_ranks = self.ranks()
        return OrderedDict((node, sorted(self.descendants(node), key=lambda _: node_ranks[_])) for node in node_ranks)


# EOF
