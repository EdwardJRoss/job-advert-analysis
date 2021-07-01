import re
from typing import Dict, Generator, List, Tuple, TypeVar

import xxhash
from datasketch import LeanMinHash, MinHash, MinHashLSH

T = TypeVar("T")

WHITESPACE = re.compile("\s+")
END_SENTENCE = re.compile("[.!?]\s+")


def tokenize(s: str) -> List[str]:
    """Split a string into tokens"""
    return WHITESPACE.split(s)


def untokenize(ts: List[str]) -> str:
    """Join a list of tokens into a string"""
    return " ".join(ts)


def sentencize(s: str) -> List[str]:
    """Split a string into a list of sentences"""
    return END_SENTENCE.split(s)


def unsentencise(ts: List[str]) -> str:
    """Join a list of sentences into a string"""
    return ". ".join(ts)


def html_unsentencise(ts: List[str]) -> str:
    """Joing a list of sentences into HTML for display"""
    return "".join(f"<p>{t}</p>" for t in ts)


def minhash(seq: List[str], num_perm: int = 128) -> MinHash:
    """Return the minhash of seq using num_perm permutations"""
    m = MinHash(num_perm=num_perm, hashfunc=xxhash.xxh64_intdigest)
    for s in seq:
        m.update(s.encode("utf8"))
    return LeanMinHash(m)


def minhash_lsh_probability(s: float, bands: int, rows: int) -> float:
    """Probability of Minhash LSH returning item with similarity s"""
    return 1 - (1 - s ** rows) ** bands


def lsh_similar(
    minhashes: Dict[T, MinHash], num_perm: int, bands: int, rows: int
) -> Generator[Tuple[T, T], None, None]:
    """Yields all of similar pairs of minhashes using LSH

    minhashes - Dictionary of key to Minhash
    num_perm  - Number of permutations used in Minhash
    bands     - Number of bands to use in LSH
    rows      - Number of rows to use in LSH

    """
    lsh = MinHashLSH[T](num_perm=num_perm, params=(bands, rows))
    for i, mh in minhashes.items():
        # Check if duplicate of already seen item
        for j in lsh.query(mh):
            yield (j, i)
        # Add to the seen items
        lsh.insert(i, mh)


def subseq(seq: List[T], n: int = 1) -> List[Tuple[T, ...]]:
    """Returns all contiguous subsequences of seq of length n

    Example: subseq([1,2,3,4], n=2) == [(1,2), (2,3), (3,4)]
    """
    return [tuple(seq[i : i + n]) for i in range(0, len(seq) + 1 - n)]


def shingle(seq: List[str], n: int = 1) -> List[str]:
    """Returns all subsequences of tokens of length n"""
    return [untokenize(list(s)) for s in subseq(seq, n)]


def jaccard(a: set, b: set) -> float:
    n = len(a.intersection(b))
    return n / (len(a) + len(b) - n)


def relevance(text_a: str, text_b: str, k: int) -> float:
    bag_a = set(shingle(tokenize(text_a), k))
    bag_b = set(shingle(tokenize(text_b), k))
    return jaccard(bag_a, bag_b)
