#! /usr/bin/env python
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


import dbus
import dbus.service
from gi.repository import GLib
from lyric import Parser


from mpris import MprisPlayer
from sources.netease import NeteaseSource


bus = dbus.SessionBus()

class LyricsService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.archean.lyrics', bus=bus)
        dbus.service.Object.__init__(self, bus_name, '/org/archean/lyrics')
        
        self.source = NeteaseSource()

        self.all_player: [MprisPlayer] = {}
        self.currrent_player: MprisPlayer = None

        self.search_results: [str] = []
        self.lyric: Parser = None
        

    def find_players(self):
        all_services = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
        mpris_services = [service for service in all_services if service.startswith('org.mpris.MediaPlayer2.')]
        if len(mpris_services) > 0:
            self.all_player = {player: MprisPlayer(player) for player in mpris_services}
            self.connect_player(mpris_services[0])


    def add_players(self, name):
        self.all_player[name] = MprisPlayer(name)


    def remove_player(self, name):
        current_name = self.current_player.name
        self.next_player()
        if name == current_name:
            self.all_player.pop(name)
    

    def connect_player(self, name):
        self.all_player[name].on_metadata_change = self.search_lyric
        self.current_player = self.all_player[name]
        self.search_lyric(self.current_player.metadata)


    def disconnect_player(self, name):
        self.all_player[name].on_metadata_change = None
        self.lyric = None
    

    def search_lyric(self, metadata):
        if metadata.title != '' and metadata.artist != '':
            self.search_results = self.source.do_search(metadata)
            lyric_text = self.source.do_download(self.search_results[0].downloadinfo)
            self.lyric = Parser(lyric_text)
            

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='s')
    def current_lyric(self):
        if self.lyric is not None:
            return self.lyric.get_lyric(self.current_player.get_position() // 1000)
        return 'No Lyric.'

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='s')
    def current_player(self):
        return self.current_player.name if self.current_player else "No player."

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='as')
    def all_player(self):
        return list(self.all_player.keys())

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='s')
    def current_metadata(self):
        return f"{self.current_player.metadata}"

    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='s')
    def current_status(self):
        return f"{self.current_player.playback_status}"


    @dbus.service.method('org.archean.lyrics.Lyric', out_signature='')
    def next_player(self):
        if len(self.all_player) > 1:
            self.disconnect_player(self.current_player.name)
            names = list(self.all_player.keys())
            cur = names.index(self.current_player.name)
            self.connect_player(names[(cur + 1) % len(self.all_player)])


if __name__ == "__main__":

    service = LyricsService()
    service.find_players()

    def name_owner_changed(name, old_owner, new_owner):
        if name.startswith('org.mpris.MediaPlayer2.'):
            if new_owner:
                print(f"MPRIS player '{name}' registered.")
                service.add_players(name)
            else:
                print(f"MPRIS player '{name}' unregistered.")
                service.remove_player(name)

    bus.add_signal_receiver(name_owner_changed, 'NameOwnerChanged', 'org.freedesktop.DBus', 'org.freedesktop.DBus')

    loop = GLib.MainLoop()
    loop.run()