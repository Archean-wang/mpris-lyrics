from dataclasses import dataclass


@dataclass
class SimpleMetadata:
    title: str
    artist: str
    album: str