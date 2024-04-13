from dataclasses import dataclass


@dataclass
class SearchResult:
    sourceid: int
    downloadinfo: str
    title: str = ''
    artist: str = ''
    album: str = ''