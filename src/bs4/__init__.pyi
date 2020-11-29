from typing import IO, Union

from .element import Tag

# These types are effective; do not match implementation

class BeautifulSoup(Tag):
    def __init__(
        self,
        markup: Union[str, bytes, IO] = "",
        features=None,
        builder=None,
        parse_only=None,
        from_encoding=None,
        exclude_encodings=None,
        element_classes=None,
        **kwargs,
    ) -> None: ...
