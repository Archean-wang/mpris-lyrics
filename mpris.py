#! /usr/bin/env python3

import time
import dbus

from sources.metadata import SimpleMetadata
from utils import debounce, dbus2simple


bus = dbus.SessionBus()


class MprisPlayer:
    def __init__(self, player, _bus=None):
        self.name = player
        self.player_proxy = self.get_proxy(player)
        self.player_interface = dbus.Interface(self.player_proxy, 'org.mpris.MediaPlayer2.Player')
        
        self.playback_status = 'Stopped'
        self.last_position = 0
        self.last_position_update_time = int(time.time() * 1000 * 1000)

        self.update_metadata = debounce(self.update_metadata_origin, 300)
        self.on_metadata_change = None

        self.init()

    @staticmethod
    def get_all_mpris_player():
        all_services = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus').ListNames()
        return  [player for player in all_services if player.startswith('org.mpris.MediaPlayer2.')]


    def get_proxy(self, player):
        if player in self.get_all_mpris_player():
            proxy = bus.get_object(player, '/org/mpris/MediaPlayer2')
            return proxy
        else:
            raise Exception(f"{player} not found")

    def on_properties_changed(self, interface_name, changed_properties, invalidated_properties):
        for prop, value in changed_properties.items():
            if prop == 'PlaybackStatus':
                self.playback_status = value
            elif prop == "Metadata":
                self.update_metadata(dbus2simple(value))

    def update_metadata_origin(self, metadata):
        if metadata.title != '' and metadata.artist != '':
            self.metadata = metadata
            if self.on_metadata_change is not None:
                self.on_metadata_change(metadata)

    def get_position(self):
        now = int(time.time() * 1000 * 1000)
        if self.playback_status == 'Playing':
            return self.last_position + now - self.last_position_update_time
        return self.last_position

    def on_seeked(self, x):
        self.last_position = x
        self.last_position_update_time = int(time.time() * 1000 * 1000)

    def get_property(self, key):
        return self.player_interface.Get('org.mpris.MediaPlayer2.Player', key, dbus_interface='org.freedesktop.DBus.Properties')

    def init(self):
        self.get_metadata()
        property_interface = dbus.Interface(self.player_proxy, 'org.freedesktop.DBus.Properties')
        
        property_interface.connect_to_signal('PropertiesChanged', self.on_properties_changed)
        self.player_interface.connect_to_signal('Seeked', self.on_seeked)

    def get_metadata(self):
        metadata = self.get_property("Metadata")
        status = self.get_property("PlaybackStatus")
        position = self.get_property("Position")

        self.playback_status = str(status)
        self.on_seeked(int(position))
        self.metadata = dbus2simple(metadata)
        self.update_metadata_origin(self.metadata)

    def __str__(self):
        return self.name


if __name__ == "__main__":
    mp = MprisPlayer()
    for service in mp.get_all_mpris_player():
        print(service)