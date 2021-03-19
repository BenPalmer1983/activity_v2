import json
import zlib


fh = open('isotope_masses.txt', 'r')
fh2 = open('iso_masses.txt','w')

alpha = 'abcdefghijklmnopqrstuvwxyz'
iso_mass = {}

for line in fh:
  line_lc = line.lower()

  flag = False
  for c in alpha:
    if(c in line_lc[0:12]):
      flag = True
    f = line.strip().split('\t')

  if(flag):
    p = f[0]
    symbol = f[1]
  else:
    f = [p, symbol] + f
  f = f[0:4]

  fa = f[-1].split('(')
  f[0] = int(f[0])
  f[2] = int(f[2])
  f[-1] = float(fa[0].replace(' ',''))
  fh2.write(str(f[0]) + ',' + str(f[1]) + ',' + str(f[2]) + ',' + str(f[3]) + '\n')

  if(f[0] not in iso_mass.keys()):
    iso_mass[f[0]] = {}
  iso_mass[f[0]][f[2]] = f[3]

fh.close()
fh2.close()
  
print(iso_mass)

def save(file_path, dict):
  dat = json.dumps(xs)
  cdat = zlib.compress(dat.encode(), level=9)
  fh = open(file_path, 'wb')
  fh.write(cdat)
  fh.close()

save('isotope_mass.z', iso_mass)