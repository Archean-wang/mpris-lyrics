#! /usr/bin/env python
import dbus
import argparse


bus = dbus.SessionBus()


class LyricsClient:
    def __init__(self):
        self.obj = bus.get_object('org.archean.lyrics', '/org/archean/lyrics')
        self.interface = dbus.Interface(self.obj, 'org.archean.lyrics.Lyric')
    
    def current_lyric(self):
        return self.interface.current_lyric()
    
    def next_player(self):
        return self.interface.next_player()

    def current_player(self):
        return self.interface.current_player()

    def all_player(self):
        return [str(player) for player in self.interface.all_player()]

    def current_metadata(self):
        return self.interface.current_metadata()

    def current_status(self):
        return self.interface.current_status()


if __name__ == "__main__":
    try:
        client = LyricsClient()
    except dbus.exceptions.DBusException as e:
        raise Exception("Lyrics service unavailable.")

    parser = argparse.ArgumentParser(description='Client for LyricsServices')
    parser.add_argument("action", action="store")

    args = parser.parse_args()

    if args.action == 'lyric':
        print(client.current_lyric())
    elif args.action == 'next':
        client.next_player()
    elif args.action == 'player':
        print(client.current_player())
    elif args.action == 'all':
        print(client.all_player())
    elif args.action == 'metadata':
        print(client.current_metadata())
    elif args.action == 'status':
        print(client.current_status())