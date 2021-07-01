import logging
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile

from kaggle.api.kaggle_api_extended import KaggleApi

from job_pipeline.sources.abstract_datasource import AbstractDatasource


class KaggleDatasource(AbstractDatasource):
    dataset: str

    def __init__(self):
        self.api = KaggleApi()
        self.api.authenticate()

    # This is a bit clunky: can't handle datasets with different file types
    def download_one(self, path: Path, source: str) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.api.dataset_download_file(self.dataset, source, path=tmpdir)

            # Unzip if zipped
            zip_path = Path(tmpdir) / (source + ".zip")
            if zip_path.exists():
                logging.debug(f"Unzipping {zip_path}")
                with ZipFile(zip_path, "r") as z:
                    z.extract(source, tmpdir)
            source_path = Path(tmpdir) / source
            assert source_path.exists()

            shutil.move(str(Path(tmpdir) / source), str(path))
