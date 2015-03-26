input_path = '/Volumes/transport/data/puzzle/050714/track/050714_s13_1.csv'

class cell():
  def __init__(self, index, t, r, c):
    self.index = index
    self.t = t
    self.r = r
    self.c = c
    self.vr = 0
    self.vc = 0

cells = []

with open(input_path) as f:
  for line in f.readlines():
    line = line.rstrip().split(',')

    cells.append(cell(int(line[1]), int(line[2]), int(line[3]), int(line[4])))

ids = list(set([cell.index for cell in cells]))

v = []

for id in ids:
  cells_id = sorted(filter(lambda x: x.index==id, cells), key=lambda x: x.t)

  for i, cell in enumerate(cells_id):
    red = list(cells_id)
    del red[i]
    prev_cell = min(red, key=lambda x: abs(cell.t - x.t - 1)) if cell.t > 1 else cell

    cell.vr = cell.r - prev_cell.r
    cell.vc = cell.c - prev_cell.c

    v.append(cell)

V1 = []
V4 = []

for i in v:
  vel = ((i.vr * 0.5)**2 + (i.vc * 0.5)**2)**0.5 / 10.4

  if vel>0.0:
    if i.index in [21,22,23,24,25]:
      V4.append(vel)
    else:
      V1.append(vel)

import matplotlib.pyplot as plt

# print(V1)

plt.hist(V4, bins=50, facecolor='yellow')
plt.title('Velocity histogram for Region 4')
plt.xlabel(r'velocity ($\mu m$ / minute)')
plt.show()
