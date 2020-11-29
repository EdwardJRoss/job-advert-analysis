from typing import Generator, Tuple, Union

from .term import BNode, Literal, URIRef

IdentType = Union[URIRef, BNode, Literal]

Triple = Tuple[IdentType, IdentType, IdentType]

class Graph:
    identifier: IdentType
    def __init__(
        self, store="default", identifier=None, namespace_manager=None, base=None
    ) -> None: ...
    def parse(
        self,
        source=None,
        publicID=None,
        format=None,
        location=None,
        file=None,
        data=None,
        **args,
    ) -> Graph: ...
    def subjects(
        self, predicate: IdentType = None, object: IdentType = None
    ) -> Generator[IdentType, None, None]: ...
    def objects(
        self, predicate: IdentType = None, object: IdentType = None
    ) -> Generator[IdentType, None, None]: ...
    def predicate_objects(
        self, subject: IdentType = None
    ) -> Generator[Tuple[IdentType, IdentType], None, None]: ...
