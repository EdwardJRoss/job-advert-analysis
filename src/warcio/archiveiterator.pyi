from typing import BinaryIO, Generator

import six

from warcio.recordloader import ArcWarcRecord

BUFF_SIZE: int

class ArchiveIterator(six.Iterator):
    def __init__(
        self,
        fileobj: BinaryIO,
        no_record_parse: bool = False,
        verify_http: bool = False,
        arc2warc: bool = False,
        ensure_http_headers: bool = False,
        block_size: int = BUFF_SIZE,
        check_digests: bool = False,
    ) -> None: ...
    def __next__(self) -> ArcWarcRecord: ...
    def __iter__(self) -> Generator[ArcWarcRecord, None, None]: ...
