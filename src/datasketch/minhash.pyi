from typing import Callable, Union

import numpy as np

from datasketch.hashfunc import sha1_hash32

class MinHash:
    def __init__(
        self,
        num_perm: int = 128,
        seed: int = 1,
        hashfunc: Callable[[bytes], int] = sha1_hash32,
        hashobj=None,  # Deprecated.
        hashvalues: Union[np.Array, list] = None,
        permutations=None,
    ) -> None: ...
    def update(self, b: bytes) -> None: ...
