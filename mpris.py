#! /usr/bin/env python3

import dbus
from dataclasses import dataclass

class MprisPlayer:
    def __init__(self, _player, _bus=None):
        self.player = _player
        self.bus = _bus if _bus else dbus.SessionBus()
        self.player_proxy = self.get_proxy(_player)
        self.player_interface = dbus.Interface(self.player_proxy, 'org.mpris.MediaPlayer2.Player')
            
    @staticmethod
    def get_all_mpris_player(bus):
        all_services = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
        return  [player for player in all_services if player.startswith('org.mpris.MediaPlayer2.')]


    def get_proxy(self, player):
        if player in self.get_all_mpris_player(self.bus):
            # 创建播放器的代理对象
            proxy = self.bus.get_object(player, '/org/mpris/MediaPlayer2')
            return proxy
        else:
            raise Exception(f"没有找到支持 MPRIS 播放器: {player}")

    def get_property(self, key):
        return self.player_interface.Get('org.mpris.MediaPlayer2.Player', key, dbus_interface='org.freedesktop.DBus.Properties')


@dataclass
class MprisMetadata:
    title: str
    artist: [str]
    album: str


if __name__ == "__main__":
    bus = dbus.SessionBus()
    mp = MprisPlayer()
    for service in mp.get_all_mpris_player():
        print(service)