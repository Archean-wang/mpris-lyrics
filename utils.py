from gi.repository import GLib
from sources.metadata import SimpleMetadata

def debounce(fn, ms):
    def wrapper(*args, **kwargs):
        if wrapper.timer is not None:
            GLib.source_remove(wrapper.timer)
        wrapper.timer = GLib.timeout_add(ms, fn, *args, **kwargs)
    wrapper.timer = None
    return wrapper


def dbus2simple(metadata):
    """
        convert dbus metadata to SimpleMetadata
    """
    title = ''
    artist = ''
    album = ''

    if "xesam:title" in metadata:
        title = metadata["xesam:title"]
    if "xesam:artist" in metadata and len(metadata['xesam:artist']) > 0:
        artist = metadata['xesam:artist'][0]
    if 'xesam:album' in metadata:
        album = metadata['xesam:album']
    return SimpleMetadata(title, artist, album)