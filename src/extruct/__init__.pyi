from typing import Any, Dict, List

SYNTAXES: List[str]

def extract(
    htmlstring: bytes,
    base_url: str = None,
    encoding: str = "UTF-8",
    syntaxes: List[str] = SYNTAXES,
    errors: str = "strict",
    uniform: bool = False,
    return_html_node: bool = False,
    schema_context: str = "http://schema.org",
    with_og_array: bool = False,
    **kwargs,
) -> Dict[str, List[Dict[str, Any]]]: ...
