# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
from skimage import filter as ft
from scipy.misc import imsave, imread
from scipy.optimize import curve_fit

class Marker():
  def __init__(self, i, track, frame, r, c):
    self.i = i
    self.track = track
    self.frame = frame
    self.r = r
    self.c = c

class CellInstance():
  def __init__(self, frame, object_number, r, c, area):
    self.marker = -1
    self.frame = frame
    self.object_number = object_number
    self.r = r
    self.c = c
    self.area = area
    self.vr = 0
    self.vc = 0

  def coords(self, rmop, cmop):
    return [self.r * rmop, self.c * cmop]

  def time(self, tpf):
    return self.frame * tpf

  def A(self, rmop, cmop):
    return self.area * rmop * cmop

  def track(self, markers):
    marker = list(filter(lambda m:m.i==self.marker, markers))[0]
    return marker.track

  def get_marker(self, markers):
    return list(filter(lambda m: m.i==self.marker, markers))[0]

  def velocity(self, rmop, cmop, tpf):
    return np.sqrt((self.vr * rmop)**2 + (self.vc * cmop)**2) / tpf

  def __str__(self):
    return '{} {} {} {} {}'.format(self.object_number, self.frame, self.r, self.c, self.area)

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='13', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    > Use masks to build up larger masks surrounding markers

    2. What data structures are input?
    > Mask, Gon

    3. What data structures are output?
    > Channel, Gon, Mask

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. load mask gons
    2. stack vertically in single array

    '''

    # vars
    path = '/Volumes/transport/data/puzzle/050714/track/050714_s13_n1.xls'
    data_path = '/Volumes/transport/data/puzzle/050714/img/out_auto'
    out = '/Volumes/transport/data/puzzle/050714/track/'
    tpf = 10.7003
    rmop = 0.5369
    cmop = 0.5369

    # open as normal
    markers = []
    with open(path, 'rb') as track_file:
      lines = track_file.read().decode('mac-roman').split('\n')[1:-1]
      for line in lines:
        line = line.split('\t')

        # details
        track = int(float(line[1]))
        frame = int(float(line[2])) - 1
        r = int(float(line[4]))
        c = int(float(line[3]))

        if len(markers)==0:
          markers.append(Marker(0, track, frame, r, c))
        else:
          i_marker = max(markers, key=lambda m: m.i)
          i = i_marker.i + 1
          markers.append(Marker(i, track, frame, r, c))

    # open measurements file and associate each marker to an area and true position
    cell_instances = []
    with open(os.path.join(data_path, 'Cells.csv')) as cell_file:
      lines = list(cell_file.readlines())[1:]
      for line in lines:
        line = line.split(',')

        # details
        frame = int(float(line[0])) - 1
        object_number = int(float(line[1]))
        r = int(float(line[4]))
        c = int(float(line[3]))
        area = int(float(line[2]))

        cell_instances.append(CellInstance(frame, object_number, r, c, area))

    for frame in range(89):
      frame_markers = list(filter(lambda m: m.frame==frame, markers))
      frame_cell_instances = list(filter(lambda c: c.frame==frame, cell_instances))

      mask_img = imread(os.path.join(data_path, 'primary_t{}.tiff'.format(str(frame) if frame>=10 else ('0' + str(frame)))))

      ids = []
      for marker in frame_markers:
        ci = mask_img[marker.r, marker.c]
        if len(list(filter(lambda c: c.object_number==ci, frame_cell_instances)))!=0:
          cell_instance = list(filter(lambda c: c.object_number==ci, frame_cell_instances))[0]
          cell_instance.marker = marker.i

    # make tracks
    tracks = list(set([marker.track for marker in markers]))

    fig = plt.figure()
    ax_v = fig.add_subplot(121)
    ax_v.set_title('velocity')
    ax_a = fig.add_subplot(122)
    ax_a.set_title('area')

    for track in tracks:
      track_cell_instances = list(filter(lambda c: c.track(markers)==track, cell_instances))

      previous_cell_instance = None
      time = []
      v = []
      a = []
      for i, cell_instance in enumerate(sorted(track_cell_instances, key=lambda c: c.frame)):
        if previous_cell_instance is None:
          cell_instance.vr = 0
          cell_instance.vc = 0
        else:
          cell_instance.vr = int((cell_instance.r - previous_cell_instance.r) / (cell_instance.frame - previous_cell_instance.frame))
          cell_instance.vc = int((cell_instance.c - previous_cell_instance.c) / (cell_instance.frame - previous_cell_instance.frame))

        previous_cell_instance = cell_instance
        time.append(cell_instance.time(tpf))
        v.append(cell_instance.velocity(rmop, cmop, tpf))
        a.append(cell_instance.A(rmop, cmop))

      ax_v.scatter(time, v)
      ax_a.scatter(time, a)

    plt.show()
