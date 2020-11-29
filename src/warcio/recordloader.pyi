from typing import Dict, Union

from warcio.bufferedreaders import BufferedReader
from warcio.limitreader import LimitReader

class ArcWarcRecord(object):
    def content_stream(self) -> Union[BufferedReader, LimitReader]: ...
    rec_headers: Dict[str, str]
