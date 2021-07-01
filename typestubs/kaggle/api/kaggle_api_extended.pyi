from pathlib import Path
from typing import Optional, Union

Pathlike = Union[str, Path]

class KaggleApi:
    def authenticate(self) -> None: ...
    def dataset_download_files(
        self,
        dataset: str,
        path: Optional[Pathlike] = None,
        force: bool = False,
        quiet: bool = True,
        unzip: bool = False,
    ) -> None: ...
