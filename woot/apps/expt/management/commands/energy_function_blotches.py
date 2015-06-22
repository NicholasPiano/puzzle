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
from scipy.stats.mstats import mode

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
    # Z = exposure.rescale_intensity(Z * 1.0)

    print('loading mean...')
    M = imread(os.path.join(base_output_path, 'mean.png'))
    M = exposure.rescale_intensity(M * 1.0)

    # define energy function based on distance from random point and z difference
    # 1. z difference (not profile joining points)
    # 2. gfp profile joining points
    # 3. bf profile joining points
    # 4. gfp strength profile joining points
    start_r, end_r, start_c, end_c = 395, 506, 305, 415
    size_r, size_c = end_r - start_r, end_c - start_c
    gfp = gfp[start_r:end_r,start_c:end_c,:]
    bf = bf[start_r:end_r,start_c:end_c,:]
    Z = Z[start_r:end_r,start_c:end_c]
    M = M[start_r:end_r,start_c:end_c]

    labels = np.zeros((Z.shape[0], Z.shape[1], 3))
    label_img = np.zeros(Z.shape)

    while (labels[:,:,0]==0).sum() > 0: # while there are more points to pick

      # 1. pick random point
      r0, c0 = randint(0, size_r-1), randint(0, size_c-1)
      z = int(series.zs * Z[r0,c0] / 255.0 - 1)
      label = labels[r0,c0,0] if labels[r0,c0,0] != 0 else labels.max() + 1 # new label if not already in place

      # 2. loop to pick other points around it with a gaussian probability. While in same label as first point, keep picking more secondary points.
      is_same_label = True
      while is_same_label:

        # pick new point
        point = np.random.multivariate_normal(mean, cov, 1).astype(int)
        r1, c1 = point[0,0] + r0, point[0,1] + c0
        r1 = (r1 if r1 < size_r else size_r - 1) if r1 >= 0 else 0
        c1 = (c1 if c1 < size_c else size_c - 1) if c1 >= 0 else 0

        while (labels[r1,c1,:]==0).sum()==0: # no slots left
          point = np.random.multivariate_normal(mean, cov, 1).astype(int)
          r1, c1 = point[0,0] + r0, point[0,1] + c0
          r1 = (r1 if r1 < size_r else size_r - 1) if r1 >= 0 else 0
          c1 = (c1 if c1 < size_c else size_c - 1) if c1 >= 0 else 0

        # draw line
        d = int(np.sqrt((r0-r1)**2 + (c0-c1)**2))
        r_line, c_line = np.linspace(r0, r1, d), np.linspace(c0, c1, d)
        line = np.vstack((r_line, c_line))

        # 3. get distributions of bf, gfp, and z between points, classify (same label or new)
        bf_distribution = map_coordinates(bf[:,:,z], line)
        gfp_distribution = map_coordinates(gfp[:,:,z], line)
        z_distribution = map_coordinates(Z, line)
        m_distribution = map_coordinates(M, line)

        # 4. make decision and assign labels
        is_same_label = np.std(z_distribution)<3

        slot = np.argmin(labels[r1,c1,:])
        labels[r1,c1,slot] = label if is_same_label else labels[r1,c1,slot]

      print('{}\t{}'.format(label, (labels[:,:,0]==0).sum()))

    # 5. print final image with mode of each column
    label_img = mode(labels, axis=2)

    plt.imshow(label_img, cmap=Greys_r)
    plt.show()
