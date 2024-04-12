from gi.repository import GLib
from functools import partial

def debounce(fn, ms):
    def wrapper(*args, **kwargs):
        if wrapper.timer is not None:
            GLib.source_remove(wrapper.timer)
        fn_with_params = partial(fn, *args, **kwargs)
        wrapper.timer = GLib.timeout_add(ms, fn_with_params)
    wrapper.timer = None
    return wrapper