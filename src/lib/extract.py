from typing import Any, Dict, Generator, List

import sources.careers_vic
import sources.cgcrecruitment
import sources.csiro
import sources.davidsonwp
import sources.engineeringjobs
import sources.ethicaljobs
import sources.gumtree
import sources.iworkfornsw
import sources.launchrecruitment
import sources.probono
import sources.seek
from sources.abstract_datasource import AbstractDatasource
from warcio.recordloader import ArcWarcRecord

DATASOURCES: List[AbstractDatasource] = [
    sources.careers_vic.Datasource(),
    sources.cgcrecruitment.Datasource(),
    sources.csiro.Datasource(),
    sources.davidsonwp.Datasource(),
    sources.engineeringjobs.Datasource(),
    sources.ethicaljobs.Datasource(),
    sources.gumtree.Datasource(),
    sources.iworkfornsw.Datasource(),
    sources.launchrecruitment.Datasource(),
    sources.probono.Datasource(),
    sources.seek.Datasource(),
]


HANDLERS = {source.name: source for source in DATASOURCES}

# TODO: datatype should be enum/list?
def extract_warc(
    warc: ArcWarcRecord, parser: str
) -> Generator[Dict[str, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers["WARC-Target-URI"]
    view_date = warc.rec_headers["WARC-Date"]
    assert uri is not None
    assert view_date is not None

    data = HANDLERS[parser].extract(html, uri, view_date)

    for datum in data:
        yield datum


def normalise_warc(data: Dict[str, Any], parser: str):
    normalise = HANDLERS[parser].normalise
    return normalise(**data)
