from typing import IO, Any, Dict, Generator, List, Optional, Union

class PageElement:
    @property
    def next_siblings(self) -> Generator[PageElement, None, None]: ...

class Tag(PageElement):
    def select_one(
        self, selector: str, namespaces: Optional[Dict[str, str]] = None, **kwargs: str
    ) -> Optional[Tag]: ...
    def select(
        self, selector: str, namespaces: Optional[Dict[str, str]] = None, **kwargs: str
    ) -> List[Tag]: ...
    def get_text(
        self,
        separator: str = "",
        strip: bool = False
        # types=(NavigableString, CData)
    ) -> str: ...
    def find(
        self, name: Optional[str] = None, attrs={}, recursive=True, text=None, **kwargs
    ) -> Optional[PageElement]: ...
    def find_all(
        self,
        name: Optional[str] = None,
        attrs={},
        recursive=True,
        text=None,
        limit=None,
        **kwargs,
    ) -> List[PageElement]: ...

class NavigableString:
    pass
