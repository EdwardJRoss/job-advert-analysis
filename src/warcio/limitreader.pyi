from typing import Optional

class LimitReader(object):
    def read(self, length: Optional[int] = None) -> bytes: ...
