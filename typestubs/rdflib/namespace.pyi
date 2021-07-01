from .term import URIRef

RDF: ClosedNamespace

class ClosedNamespace:
    def __getattr__(self, name: str) -> URIRef: ...

class Namespace(str):
    def __getitem__(self, key) -> URIRef: ...
