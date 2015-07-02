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

    for frame in range(89):
      frame_markers = list(filter(lambda m: m.frame==frame, markers))
      mask_img = imread(os.path.join(data_path, 'primary_t{}.tiff'.format(str(frame) if frame>=10 else ('0' + str(frame)))))

      for marker in frame_markers:
        ci = mask_img[marker.r, marker.c]
