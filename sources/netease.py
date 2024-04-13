import requests
import json

from .result import SearchResult


NETEASE_HOST = 'https://music.163.com'
NETEASE_SEARCH_URL = '/api/search/get'
NETEASE_LYRIC_URL = '/api/song/lyric'


class NeteaseSource():
    """ Lyric source from music.163.com
    """

    def __init__(self):
        self.id = 'netease'

    def do_search(self, metadata):
        keys = []
        if metadata.title:
            keys.append(metadata.title)
        if metadata.artist:
            keys.append(metadata.artist)
        url = NETEASE_HOST + NETEASE_SEARCH_URL
        urlkey = '+'.join(keys).replace(' ', '+')
        params = f's={urlkey}&type=1'
        res = requests.post(url=url, params=params)
        
        if res.status_code < 200 or res.status_code  >= 400:
            raise Exception(res.status_code , '')

        def map_func(song):
            if song['artists']:
                artist_name = song['artists'][0]['name']
            else:
                artist_name = ''
            url = NETEASE_HOST + NETEASE_LYRIC_URL + '?id=' + str(song['id']) + '&lv=-1&kv=-1&tv=-1'
            return SearchResult(title=song['name'],
                                artist=artist_name,
                                album=song['album']['name'],
                                sourceid=self.id,
                                downloadinfo=url)

        parsed = res.json()
        result = list(map(map_func, parsed['result']['songs']))

        
        song_count = parsed['result']['songCount']
        if song_count > 10:
            params = params + '&offset=10'
            res = requests.post(url=url, params=params)
        if res.status_code < 200 or res.status_code >= 400:
            raise hException(res.status_code, '')
        parsed = res.json()
        result = result + list(map(map_func, parsed['result']['songs']))
        return result

    def do_download(self, downloadinfo, attempt_use_translation=False):
        res = requests.get(url=downloadinfo)
        if res.status_code < 200 or res.status_code >= 400:
            raise Exception(status)

        parsed = res.json()
        if 'nolyric' in parsed or 'uncollected' in parsed:
            raise ValueError('This item has no lyrics.')

        if attempt_use_translation:
            lyric = parsed['tlyric']['lyric']
            if not lyric:
                lyric = parsed['lrc']['lyric']
        else:
            lyric = parsed['lrc']['lyric']

        return lyric
