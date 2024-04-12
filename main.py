#! /usr/bin/env python
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


import time
import dbus
import dbus.service
from gi.repository import GLib
from lyric import Parser


from mpris import MprisPlayer, MprisMetadata
from netease import NeteaseSource, Metadata
from utils import debounce

# 创建一个 D-Bus 实例，连接到会话总线
bus = dbus.SessionBus()

class Lyrics(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.archean.lyrics', bus=bus)
        dbus.service.Object.__init__(self, bus_name, '/org/archean/lyrics')
        
        self.source = NeteaseSource()

        self.all_player: [MprisPlayer] = []
        self.currrent_player: MprisPlayer = None

        self.playback_status = 'Stopped'

        self.search_lyrics = []
        self.lyric = None
        
        self.last_position = 0
        self.last_position_update_time = int(time.time() * 1000 * 1000)

        self.update_metadata = debounce(self.update_metadata_origin, 300)

    def find_players(self):
        all_service = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
        self.all_player = [MprisPlayer(player) for player in all_service if player.startswith('org.mpris.MediaPlayer2.')]
        if len(self.all_player) > 0:
            self.set_player(self.all_player[0])

    def on_properties_changed(self, interface_name, changed_properties, invalidated_properties):
        for prop, value in changed_properties.items():
            if prop == 'PlaybackStatus':
                self.playback_status = value
            elif prop == "Metadata":
                if 'xesam:artist' in value and value['xesam:artist'][0] != '':
                    self.update_metadata(MprisMetadata(str(value['xesam:title']), [str(i) for i in value['xesam:artist']], str(value['xesam:album'])))
    
    def update_metadata_origin(self, metadata):
        self.search_lyrics = self.source.do_search(Metadata(metadata.title, metadata.artist[0]))
        select = self.search_lyrics[0]
        lyric = self.source.do_download(select._downloadinfo)
        self.lyric = Parser(lyric)

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='s')
    def current_lyric(self):
        if self.lyric is not None:
            return self.lyric.get_lyric(self.get_position() // 1000)
        return 'No Lyric.'

    def on_seeked(self, x):
        self.last_position = x
        self.last_position_update_time = int(time.time() * 1000 * 1000)

    def get_position(self):
        now = int(time.time() * 1000 * 1000)
        if self.playback_status == 'Playing':
            return self.last_position + now - self.last_position_update_time
        return self.last_position

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='')
    def next_player(self):
        if len(self.all_player) > 2:
            cur = self.all_player.index(self.current_player)
            self.set_player(self.all_player[(cur + 1) % len(self.all_player)])

    def set_player(self, player):
        self.current_player = player
        self.get_metadata()
        player_proxy = self.current_player.player_proxy
        
        player_interface = dbus.Interface(player_proxy, 'org.mpris.MediaPlayer2.Player')
        property_interface = dbus.Interface(player_proxy, 'org.freedesktop.DBus.Properties')
        
        property_interface.connect_to_signal('PropertiesChanged', self.on_properties_changed)
        player_interface.connect_to_signal('Seeked', self.on_seeked)

    def get_metadata(self):
        metadata = self.current_player.get_property("Metadata")
        status = self.current_player.get_property("PlaybackStatus")
        position = self.current_player.get_property("Position")

        self.playback_status = str(status)
        self.on_seeked(position)
        self.update_metadata_origin(MprisMetadata(str(metadata['xesam:title']), [str(i) for i in metadata['xesam:artist']], str(metadata['xesam:album'])))



if __name__ == "__main__":
    lyrics = Lyrics()
    lyrics.find_players()

    def name_owner_changed(name, old_owner, new_owner):
        if name.startswith('org.mpris.MediaPlayer2.'):
            lyrics.find_players()
            if new_owner:
                print(f"MPRIS player '{name}' registered.")
            else:
                print(f"MPRIS player '{name}' unregistered.")

    # 监听 NameOwnerChanged 信号
    bus.add_signal_receiver(name_owner_changed, 'NameOwnerChanged', 'org.freedesktop.DBus', 'org.freedesktop.DBus')

    # 进入事件循环
    loop = GLib.MainLoop()
    loop.run()