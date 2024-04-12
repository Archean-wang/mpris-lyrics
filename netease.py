import requests
import json


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
        params = 's=%s&type=1' % urlkey

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




class SearchResult:
    """ Lyrics that match the metadata to be searched.
    """

    def __init__(self, sourceid, downloadinfo, title='', artist='', album='', comment=''):
        """

        Arguments:
        - `title`: The matched lyric title.
        - `artist`: The matched lyric artist.
        - `album`: The matched lyric album.
        - `downloadinfo`: Some additional data that is needed to download the
          lyric. Normally this value is the url or ID of the lyric.
          ``downloadinfo`` MUST be composed with basic types such as numbers,
          lists, dicts or strings so that it can be converted to D-Bus compatible
          dict with `to_dict` method.
        """
        self._title = title
        self._artist = artist
        self._album = album
        self._comment = comment
        self._sourceid = sourceid
        self._downloadinfo = downloadinfo

    def to_dict(self, ):
        """ Convert the result to a dict so that it can be sent with D-Bus.
        """
        return {'title': self._title,
                'artist': self._artist,
                'album': self._album,
                'comment': self._comment,
                'sourceid': self._sourceid,
                'downloadinfo': self._downloadinfo}

    def __str__(self):
        return f"""title: {self._title},
                artist: {self._artist},
                album: {self._album},
                comment: {self._comment},
                sourceid: {self._sourceid},
                downloadinfo: {self._downloadinfo}"""


class Metadata:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist