from typing import Any, Dict, Generator
from warcio.recordloader import ArcWarcRecord
import sources.careers_vic, sources.cgcrecruitment, sources.csiro, \
    sources.davidsonwp, sources.engineeringjobs, sources.ethicaljobs, \
    sources.gumtree, sources.iworkfornsw, sources.launchrecruitment, \
    sources.probono, sources.seek

DATASOURCES = [
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


HANDLERS = {source.name: {'extract': source.extract, 'normalise': source.normalise}
            for source in DATASOURCES}

# TODO: datatype should be enum/list?
def extract_warc(warc: ArcWarcRecord, parser: str) -> Generator[Dict[str, Any], None, None]:
    html = warc.content_stream().read()
    uri = warc.rec_headers['WARC-Target-URI']
    view_date = warc.rec_headers['WARC-Date']
    assert uri is not None
    assert view_date is not None

    data = HANDLERS[parser]['extract'](html, uri, view_date)

    for datum in data:
        yield datum

def normalise_warc(data: Dict[str, Any], parser: str):
    normalise = HANDLERS[parser]['normalise']
    return normalise(**data)
