from typing import Dict, Generic, Hashable, List, Tuple, TypeVar

from datasketch import MinHash

T = TypeVar("T")

class MinHashLSH(Generic[T]):
    def __init__(
        self,
        threshold: float = 0.9,
        num_perm: int = 128,
        weights: Tuple[float, float] = (0.5, 0.5),
        params: Tuple[int, int] = None,
        storage_config: Dict = None,
        prepickle: bool = None,
    ) -> None: ...
    def insert(
        self, key: T, minhash: MinHash, check_duplication: bool = True
    ) -> None: ...
    def query(self, minhash: MinHash) -> List[T]: ...
