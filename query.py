"""
  Get current lyric
"""
import dbus

bus = dbus.SessionBus()
try:
  obj = bus.get_object('org.archean.lyrics', '/org/archean/lyrics')
  interface = dbus.Interface(obj, 'org.archean.lyrics.Lyric')
  print(interface.current_lyric())
except dbus.exceptions.DBusException as e:
  print("Lyrics service unavailable.")