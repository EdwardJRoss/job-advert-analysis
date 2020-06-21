from typing import Generator, FrozenSet, Dict, List, Any, Iterable
import re
from itertools import groupby
import rdflib

WEB_DATA_COMMONS_JOB_POSTINGS = [
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2013-11/quads/schemaOrgDatasetsByPage/schemaorgJobPosting.nq.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2014-12/quads/ClassSpecificQuads/schemaorgJobPosting.nq.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2015-11/quads/classspecific/schema_JobPosting.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2016-10/quads/classspecific/schema_JobPosting.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2017-12/quads/classspecific/schema_JobPosting.gz',
    # From 2018 onwards Have json-ld as well
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2018-12/quads/classspecific/md/schema_JobPosting.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2018-12/quads/classspecific/json/schema_JobPosting.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2019-12/quads/classspecific/md/schema_JobPosting.gz',
    'http://data.dws.informatik.uni-mannheim.de/structureddata/2019-12/quads/classspecific/json/schema_JobPosting.gz',
]

RDF_TYPE_URI = rdflib.term.URIRef(
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")


RDF_QUAD_LABEL_RE = re.compile("[ \t]+<([^>]*)>[ \t].\n$")
def get_quad_label(line: str) -> str:
    """Returns the content of an IRI Label of a single N-Quad

    By the specification (https://www.w3.org/TR/n-quads/) a Quad does 
    not need to have a label, and a label can be an IRI or a Blank Node.

    This function requires that the label exists and is an IRI.

    > get_quad_label('<subject> <predicate> "an object" <http://example.org/label> .\n')
    >> 'http.example.org/label'
    """
    return RDF_QUAD_LABEL_RE.search(line).group(1)

def parse_nquads(lines: Iterable[str]) -> Generator[rdflib.Graph, None, None]:
    for group, quad_lines in groupby(lines, get_quad_label):
        graph = rdflib.Graph(identifier=group)
        graph.parse(data=''.join(quad_lines), format='nquads')
        yield graph


def get_blanks_of_type(
    graph: rdflib.Graph, rdf_type: rdflib.term.URIRef
) -> Generator[rdflib.term.BNode, None, None]:
    """Generates all Blank Nodes with a given type in RDF syntax"""
    for subject in graph.subjects(RDF_TYPE_URI, rdf_type):
        if type(subject) == rdflib.term.BNode:
            yield subject


def get_job_postings(graph: rdflib.Graph) -> Generator[rdflib.term.BNode, None, None]:
    """Generates all Blank nodes that are schema.org JobPostings in the graph"""
    return get_blanks_of_type(graph, rdflib.term.URIRef("http://schema.org/JobPosting"))


def get_blank_subjects(graph: rdflib.Graph) -> FrozenSet[rdflib.term.BNode]:
    """Returns all blank subjects in graph"""
    return frozenset(s for s in graph.subjects() if type(s) == rdflib.term.BNode)


def get_blank_objects(graph: rdflib.Graph) -> FrozenSet[rdflib.term.BNode]:
    """Returns all blank objects in graph"""
    return frozenset(o for o in graph.objects() if type(o) == rdflib.term.BNode)


def get_root_blanks(graph: rdflib.Graph) -> FrozenSet[rdflib.term.BNode]:
    """Returns all blank nodes that are not objects of any triple"""
    return get_blank_subjects(graph) - get_blank_objects(graph)


class CycleError(Exception):
    pass


def _graph_to_dict(
    graph: rdflib.graph.Graph, root: rdflib.term.BNode, seen: frozenset = frozenset()
) -> Dict[str, List[Any]]:
    result = {}  # type: Dict[str, List[Any]]
    for predicate, obj in graph.predicate_objects(root):
        predicate = predicate.toPython()
        if obj in seen:
            raise CycleError(
                f"Cyclic reference to {obj} in {graph.identifier}")
        elif type(obj) == rdflib.term.BNode:
            obj = _graph_to_dict(graph, obj, seen.union([obj]))
        else:
            obj = obj.toPython()
        result[predicate] = result.get(predicate, []) + [obj]
    return result

def graph_to_dict(graph: rdflib.graph.Graph, root: rdflib.term.BNode) -> Dict[str, List[Any]]:
    """Returns a dictionary mapping predicates to lists of objects

    Every Blank node is recursively mapped into a dictionary of predicates to lists of objects.
    Raises a CycleError if the objects of a Blank Node contains the node itself.
    """
    result = _graph_to_dict(graph, root)
    result['_label'] = [graph.identifier.toPython()]
    return result


def extract_nquads_of_type(lines: Iterable[str], rdf_type: rdflib.term.URIRef) -> Generator[Dict[str, List[Any]], None, None]:
    for graph in parse_nquads(lines):
        for node in get_blanks_of_type(graph, rdf_type):
            yield graph_to_dict(graph, node)
