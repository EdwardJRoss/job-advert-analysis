from datasketch import MinHash

class LeanMinHash(MinHash):
    def __init__(
        self, minhash: MinHash = None, seed: int = None, hashvalues=None
    ) -> None: ...
