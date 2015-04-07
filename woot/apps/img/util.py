# apps.img.util

# django

# local

# util
import numpy as np

def cut_to_black(array):
  # coordinates of non-black
  r0 = np.argmax(np.any(array, axis=1))
  r1 = array.shape[0] - np.argmax(np.any(array, axis=1)[::-1])
  c0 = np.argmax(np.any(array, axis=0))
  c1 = array.shape[1] - np.argmax(np.any(array, axis=0)[::-1])

  # return cut
  return array[r0:r1,c0:c1]

# for point, distance in spiral(centre=marker.centre(), direction='+r', gap=1, steps=10):

# def sign(i):
#   return -1 if i<0 else 1
#
# class Spiral():
#   def __init__(self, origin=(0,0), primary=0, target=1, size=1):
#     self.origin = _Point(None, None, origin[0], origin[1], 0)
#     self.current = self.origin
#     self.primary = primary
#     self.target = target
#     self.size = size
#     self.points = []
#
#   def step(self, steps):
#     while step < steps:
#       next_point = _Point(self.origin, self.current, 0, 0)
#       if self.current.primary==self.target:
#         if self.current.secondary==self.target:
#           self.target = -(self.target + sign(self.target))
#           next_point.primary = current.primary + sign(self.target)
#         else:
#           next_point.secondary = current.secondary + sign(self.target)
#       else:
#         next_point.primary = current.primary + sign(self.target)
#       self.points.append(next_point)
#       self.current = next_point
#
#     return self.current
#
#
#
# class _Point():
#   def __init__(self, origin, previous, primary, secondary, s):
#     self.origin = origin
#     self.previous = previous
#     self.primary = primary
#     self.secondary = secondary
#     self.s = s

#
# class Coord():
#   def __init__(self, origin, r, c):
#     self.origin = origin
#     self.r = r
#     self.c = c
#
#   def d(self):
#     return np.sqrt((origin.r - self.r)**2 + (origin.c - self.c)**2)
#
#   def t(self):
#     return ((self.r, self.c), self.d())

# origin = Coord(centre, centre[0], centre[1])
# start = Coord(origin, {'+r':gap, '-r':-gap, '+c':0, '-c':0}[direction], {'+r':0, '-r':0, '+c':gap, '-c':-gap}[direction])
# second = Coord(origin, {'+r':gap, '-r':-gap, '+c':0, '-c':0}[direction], {'+r':0, '-r':0, '+c':gap, '-c':-gap}[direction])




def spiral():

  spiral = []

  steps = 100
  step = 0
  target = -1
  origin = [0,0]
  coord = [0,0]

  while step < steps:
    if coord[0]==target:
      if coord[1]==target:
        target = -(target + sign(target))
        coord[0] += sign(target)
      else:
        coord[1] += sign(target)
    else:
      coord[0] += sign(target)
    spiral.append(coord.copy())
    step += 1

  return spiral
