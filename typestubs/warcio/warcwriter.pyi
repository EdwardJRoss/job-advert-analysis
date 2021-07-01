from typing import BinaryIO

from warcio.recordloader import ArcWarcRecord

class WARCWriter:
    def __init__(self, filebuf: BinaryIO, *args, **kwargs) -> None: ...
    def write_record(self, record: ArcWarcRecord, params=None) -> None: ...
