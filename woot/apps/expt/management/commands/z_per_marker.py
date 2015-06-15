# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option
from scipy.ndimage.filters import gaussian_filter as gf
from scipy.ndimage.filters import laplace
from scipy.ndimage import map_coordinates
import matplotlib.pyplot as plt
from scipy.misc import imread, imsave
from skimage import exposure
from random import random

### data structures
class Distribution():
  def __init__(self, r, c, data, max_value, mean_value, min_value, z, is_marker):
    self.r = r
    self.c = c
    self.data = data
    self.max_value = max_value
    self.mean_value = mean_value
    self.min_value = min_value
    self.z = z
    self.is_marker = is_marker

# methods
def scan_point(img, rs, cs, r, c, size=3):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size if r + size <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size if c + size <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

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
    '''

    # setup
    def create_path(path):
      if not os.path.exists(path):
        os.mkdir(path)

    base_output_path = '/Volumes/transport/profile/'
    create_path(base_output_path)

    # definitions
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()
    t = 0

    # 1. load gfp and brightfield gons at timestep
    # gfp_gon = composite.gons.get(t=t, channel__name='0')
    # gfp = gfp_gon.load()
    # gfp = exposure.rescale_intensity(gfp * 1.0)
    # gfp = gf(gfp, sigma=3)
    #
    # bf_gon = composite.gons.get(t=t, channel__name='0').gons.get(z=37)
    # bf = bf_gon.load()
    Z = imread(os.path.join(base_output_path, 'z_smooth2.png'))

    # print z values for each cell
    for cell_instance in series.cell_instances.filter(t=t):
      # r,c
      r, c = cell_instance.r, cell_instance.c

      # z
      z = Z[r,c]

      # select all locations in the image with corresponding z
      z_img = np.zeros(Z.shape)
      z_img[Z==z-1] = 1
      z_img[Z==z] = 1
      z_img[Z==z+1] = 1

      plt.imshow(z_img)
      plt.show()
      plt.cla()
