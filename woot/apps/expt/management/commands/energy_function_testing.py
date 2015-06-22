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

    print('loading mask...')
    mask = imread(os.path.join(base_output_path, 'mask_lower.png'))
    mask = exposure.rescale_intensity(mask * 1.0)

    label_img = np.zeros(Z.shape)

    # define energy function based on distance from random point and z difference
    # 1. z difference (not profile joining points)
    # 2. gfp profile joining points
    # 3. bf profile joining points
    # 4. gfp strength profile joining points

    # 1. pick random point, set label value and update label array
    # define point for now
    ci1 = series.cell_instances.get(pk=5059)
    r, c = 465, 352
    z_value = Z[r,c]
    # z = int(series.zs * z_value / 255.0)
    z = 37

    gfp_edge = ft.canny(gfp[:,:,z], sigma=2)
    bf_edge = ft.canny(bf[:,:,z], sigma=2)
    Z_edge = ft.canny(Z, sigma=2)
    M_edge = ft.canny(M, sigma=2)
    mask_edge = ft.canny(mask, sigma=2)

    ax_bf = plt.subplot(231)
    ax_bf.set_ylim([-0.1,1.1])
    ax_bf.set_title('bf')
    ax_gfp = plt.subplot(232)
    ax_gfp.set_ylim([-0.1,1.1])
    ax_gfp.set_title('gfp')
    ax_z = plt.subplot(233)
    ax_z.set_ylim([-0.1,1.1])
    ax_z.set_title('z')
    ax_m = plt.subplot(234)
    ax_m.set_ylim([-0.1,1.1])
    ax_m.set_title('m')
    ax_mean = plt.subplot(235)
    ax_mean.set_ylim([-0.1,1.1])
    ax_mean.set_title('mean')

    ax = plt.subplot(236)
    ax.imshow(bf[:,:,z]+0.1*mask, cmap='Greys_r')
    ax.scatter(c, r, c='black')

    for i in range(10):
      # 2. pick second point with gaussian probability in distance
      point = np.random.multivariate_normal(mean, cov, 1).astype(int)
      r1, c1 = point[0,0] + r, point[0,1] + c
      d = int(np.sqrt((r-r1)**2 + (c-c1)**2))
      z1_value = Z[r1,c1]
      z1 = int(series.zs * z1_value / 255.0) - z_diff
      r_line, c_line = np.linspace(r, r1, d), np.linspace(c, c1, d)
      line = np.vstack((r_line, c_line))

      # 3. get distributions of bf, gfp, and z between points, classify (same label or new)
      bf_distribution = map_coordinates(bf_edge, line)
      gfp_distribution = map_coordinates(gfp_edge, line)
      z_distribution = map_coordinates(Z_edge, line)
      m_distribution = map_coordinates(mask_edge, line)
      mean_distribution = map_coordinates(M_edge, line)

      ax_bf.plot(bf_distribution)
      ax_gfp.plot(gfp_distribution)
      ax_z.plot(z_distribution)
      ax_m.plot(m_distribution)
      ax_mean.plot(mean_distribution)
      ax.plot(c1,r1,'o')

    plt.show()
