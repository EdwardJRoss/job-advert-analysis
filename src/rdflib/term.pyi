from typing import Any

class Node:
    pass

class Identifier(Node, str):
    pass

class URIRef(Identifier):
    def toPython(self) -> str: ...

class BNode(Identifier):
    def toPython(self) -> str: ...

class Literal(Identifier):
    def toPython(self) -> Any: ...

