import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pandas as pd

from lib.io import AtomicFileWriter


def ensure_extension(path: Path, extension: Optional[str]) -> Path:
    """Returns path and appends extension if it is missing

    Raises an error if the extension does not match
    """
    if extension is None:
        return path
    assert extension.startswith(".")
    suffixes = path.suffixes
    if suffixes:
        if "".join(suffixes) == extension:
            return path
        else:
            raise ValueError(f"Unexpected extension: expected {extension}, got {path}")
    else:
        return Path(str(path) + extension)


def get_base_stem(path: Path) -> str:
    """Get filename from path removing all suffixes

    get_base_stem('foo/bar.warc.gz') == 'bar'
    """
    name = path.name
    suffix_len = len("".join(path.suffixes))
    return name[:-suffix_len]


def read_jsonl(filename: Path) -> Generator[Dict[Any, Any], None, None]:
    with open(filename, "r") as f:
        for line in f:
            yield json.loads(line)


def module_name(name):
    return name.split(".")[-1]


class AbstractDatasource(ABC):
    name: str

    # Name -> Value
    sources: Dict[str, str]

    raw_extension: Optional[str] = None

    @abstractmethod
    def download_one(self, path: Path, source: str) -> None:
        """Download source from datasource to path"""
        pass

    def download(self, path: Path, overwrite: bool = False):
        path.mkdir(parents=True, exist_ok=True)
        for source_name, source_key in self.sources.items():
            dest_path = ensure_extension(path / source_name, self.raw_extension)
            if overwrite or not dest_path.exists():
                logging.info(f"Downloading {source_name}")
                self.download_one(dest_path, source_key)
            else:
                logging.info(f"Skipping {source_name}")

    @abstractmethod
    def extract_one(self, path: Path) -> Generator[Dict[Any, Any], None, None]:
        """Extract data from one raw downloaded source"""
        pass

    def extract_all(
        self, source_dir: Path, dest_dir: Path, overwrite: bool = False
    ) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        for source_path in source_dir.glob("*" + (self.raw_extension or "")):
            name = get_base_stem(source_path)
            dest_path = ensure_extension(dest_dir / name, ".jsonl")
            if overwrite or not dest_path.exists():
                logging.info(f"Extracting {source_path} to {dest_path}")
                with AtomicFileWriter(dest_path) as output:
                    for datum in self.extract_one(source_path):
                        line = json.dumps(datum) + "\n"
                        output.write(line.encode("utf-8"))
            else:
                logging.info(f"Skipping {source_path}; {dest_path} exists")

    @abstractmethod
    def normalise(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    def normalise_all(
        self, source_dir: Path, dest_dir: Path, overwrite: bool = False
    ) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        for source_path in source_dir.glob("*.jsonl"):
            name = get_base_stem(source_path)
            dest_path = ensure_extension(dest_dir / name, ".feather")

            if overwrite or not dest_path.exists():
                logging.info(f"Normalising {source_path}")
                source_data = read_jsonl(source_path)

                normalised_data = [self.normalise(**datum) for datum in source_data]

                for datum in normalised_data:
                    datum["processor"] = self.name
                    datum["source"] = name

                # Is there a more sensible output format??
                if normalised_data:
                    df = pd.DataFrame(normalised_data)
                    df.to_feather(dest_path)
                else:
                    logging.warning("No data output for %s", dest_path)
            else:
                logging.info(f"Skipping normalising {source_path} - {dest_path} exists")
