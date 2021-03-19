import json
import zlib

class zfdict:

  def save(file_path, dict):
    dat = json.dumps(xs)
    cdat = zlib.compress(dat.encode(), level=9)
    fh = open(file_path, 'wb')
    fh.write(cdat)
    fh.close()


  def load(file_path):
    fh = open(file_path, 'rb')
    cdat = ''.encode()
    for r in fh:
      cdat = cdat + r
    fh.close()
    return json.loads(zlib.decompress(cdat).decode())











