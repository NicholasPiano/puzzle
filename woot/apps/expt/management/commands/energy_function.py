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
    mean = [0,0]
    cov = [[100,0],[0,100]]

    # 1. load gfp and brightfield gons at timestep
    print('loading gfp...')
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)
    gfp = gf(gfp, sigma=3)

    print('loading bf...')
    bf_gon = composite.gons.get(t=t, channel__name='1')
    bf = bf_gon.load()
    bf = exposure.rescale_intensity(bf * 1.0)
    print(bf.max())

    print('loading Z...')
    Z = imread(os.path.join(base_output_path, 'z_smooth2.png'))
    label_img = np.zeros(Z.shape)

    # define energy function based on distance from random point and z difference
    # 1. z difference (not profile joining points)
    # 2. gfp profile joining points
    # 3. bf profile joining points
    # 4. gfp strength profile joining points

    # 1. pick random point, set label value and update label array
    # define point for now
    ci1 = series.cell_instances.get(pk=5059)
    r, c = ci1.r, ci1.c
    z_value = Z[r,c]
    z = series.zs * int(z_value / 255.0)

    # img_size = 100
    # plt.scatter(img_size,img_size, c='r')

    for i in range(10):
      # 2. pick second point with gaussian probability in distance
      point = np.random.multivariate_normal(mean, cov, 1).astype(int)
      r1, c1 = point[0,0] + r, point[0,1] + c
      d = int(np.sqrt((r-r1)**2 + (c-c1)**2))
      z1_value = Z[r1,c1]
      z1 = series.zs * int(z1_value / 255.0)
      r_line, c_line = np.linspace(r, r1, 100), np.linspace(c, c1, 100)
      line = np.vstack((r_line, c_line))

      # 3. get distributions of bf, gfp, and z between points, classify (same label or new)
      bf_distribution = map_coordinates(bf[:,:,z], line)
      gfp_distribution = map_coordinates(gfp[:,:,z], line)
      z_distribution = map_coordinates(Z, line)

      # plt.scatter(img_size + r1 - r, img_size + c1 - c, c='b')

    # img = Z[r-img_size:r+img_size,c-img_size:c+img_size]
    # plt.imshow(img, cmap='Greys_r')
    # plt.show()
