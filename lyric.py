import re

class Parser:
  def __init__(self, lyric_text):
    self.lyric = lyric_text.strip()
    self.lyric_map = self.parse()

  def parse(self):
    lines = self.lyric.split('\n')
    pattern = re.compile('^\[(.*?)\](.*?)$')
    d = {}
    for line in lines:
      res = pattern.findall(line)
      if len(res) > 0:
        point = res[0][0]
        text = res[0][1]
        if text != '':
            m, s = point.split(':')
            second = int((int(m) * 60 + float(s)) * 1000)
            d[second] = text
    return d

  def get_lyric(self, ms):
    points = list(self.lyric_map.keys())
    for index in range(len(self.lyric_map)):
      if ms >= points[index]:
        continue
      return self.lyric_map[points[max(0, index-1)]]
    return ""