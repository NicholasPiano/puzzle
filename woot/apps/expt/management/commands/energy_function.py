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
from skimage import filter as ft
from random import random, randint

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
    z_diff = 4

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

    print('loading Z...')
    Z = imread(os.path.join(base_output_path, 'z_smooth2.png'))
    Z = exposure.rescale_intensity(Z * 1.0)

    print('loading mean...')
    M = imread(os.path.join(base_output_path, 'mean.png'))
    M = exposure.rescale_intensity(M * 1.0)

    label_img = np.zeros((Z.shape[0], Z.shape[1], 10))

    # define energy function based on distance from random point and z difference
    # 1. z difference (not profile joining points)
    # 2. gfp profile joining points
    # 3. bf profile joining points
    # 4. gfp strength profile joining points

    while (label_img[:,:,0]==0).sum() > 0:

      # 1. pick random point, set label value and update label array
      r, c = randint(0, series.rs-1), randint(0, series.cs-1)
      z = int(series.zs * Z[r,c] / 255.0)

      # next label
      label = label_img.max() + 1 if label_img[r,c,:].sum()==0 else label_img[r,c,0]
      secondary_label = label_img.max() + 1 if label_img[r,c,:].sum()==0 else label + 1

      # 2. pick second point with gaussian probability in distance
      point = np.random.multivariate_normal(mean, cov, 1).astype(int)
      r1, c1 = point[0,0] + r, point[0,1] + c
      r1 = (r1 if r1 < series.rs else series.rs - 1) if r1 >= 0 else 0
      c1 = (c1 if c1 < series.cs else series.cs - 1) if c1 >= 0 else 0

      while (label_img[r1,c1,:]==0).sum()==0: # no slots left
        point = np.random.multivariate_normal(mean, cov, 1).astype(int)
        r1, c1 = point[0,0] + r, point[0,1] + c
        r1 = (r1 if r1 < series.rs else series.rs - 1) if r1 >= 0 else 0
        c1 = (c1 if c1 < series.cs else series.cs - 1) if c1 >= 0 else 0

      # draw line
      d = int(np.sqrt((r-r1)**2 + (c-c1)**2))
      r_line, c_line = np.linspace(r, r1, d), np.linspace(c, c1, d)
      line = np.vstack((r_line, c_line))

      # 3. get distributions of bf, gfp, and z between points, classify (same label or new)
      bf_distribution = map_coordinates(bf[:,:,z], line)
      gfp_distribution = map_coordinates(gfp[:,:,z], line)
      z_distribution = map_coordinates(Z, line)
      m_distribution = map_coordinates(M, line)

      # 4. make decision and assign labels
      is_same_region = True

      slot = np.argmax(label_img[r1,c1,:])
      label_img[r1,c1,slot] = label if is_same_region else secondary_label

      print((label_img[:,:,0]==0).sum())
