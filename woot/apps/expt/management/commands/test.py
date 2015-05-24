# expt.command: step03_pmod

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *
from apps.img.util import *

# util
import os
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from skimage import filter as ft

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
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

    ### SETUP
    def create_path(path):
      if not os.path.exists(path):
        os.mkdir(path)

    base_output_path = '/Volumes/transport/demo/test/'

    create_path(base_output_path)

    # scan point
    def scan_point(gfp, r, c, size=3):
      r0 = r - size if r - size >= 0 else 0
      r1 = r + size if r + size <= gfp_gon.rs else gfp_gon.rs
      c0 = c - size if c - size >= 0 else 0
      c1 = c + size if c + size <= gfp_gon.cs else gfp_gon.cs

      column = gfp[r0:r1,c0:c1,:]
      column_1D = np.sum(np.sum(column, axis=0), axis=0)

      return column_1D

    # select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])
    ### SETUP


    ### 1. Each point in 'mask' is the mean or standard deviation of that point vertically in the GFP
    '''
    path = os.path.join(base_output_path, 'mask-projection')
    create_path(path)

    for t in range(1):
    # for t in range(composite.series.ts):

      mask = np.zeros(composite.series.shape(), dtype=float)
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      gfp = gf(gfp, sigma=2)

      for r in range(0,composite.series.rs,1):
        for c in range(0,composite.series.cs,1):
          column = scan_point(gfp, r, c)
          print(t,r,c)

          # normalise or pick plot type
          distribution = np.array(column) / np.max(column)

          mask[r,c] = (1.0 - np.mean(distribution))

      # plot
      plt.imshow(mask, cmap='jet')
      plt.savefig(os.path.join(path, 'mask_t{}.png'.format(t)))
      plt.clf()

      # further analysis
      # gradient
      # dx, dy = tuple(np.gradient(mask))
      # plt.imshow(dx, cmap='jet')
      # plt.savefig(os.path.join(path, 'mask_t{}_dx.png'.format(t)))
      # plt.clf()
      #
      # plt.imshow(dy, cmap='jet')
      # plt.savefig(os.path.join(path, 'mask_t{}_dy.png'.format(t)))
      # plt.clf()

    '''

    ### 2. Same as (1), but for each level
    '''
    path = os.path.join(base_output_path, 'mask-z')
    create_path(path)

    for t in range(1):
    # for t in range(composite.series.ts):

      mask = np.zeros(composite.series.shape(d=3), dtype=float)
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      gfp = gf(gfp, sigma=2)

      for r in range(0,composite.series.rs,1):
        for c in range(0,composite.series.cs,1):
          column = scan_point(gfp, r, c)

          # normalise or pick plot type
          distribution = np.array(column) / np.max(column)
          z = np.argmax(distribution)

          mask[r,c,z] = (1.0 - np.mean(distribution))

      for z in range(mask.shape[2]):
        plt.imshow(mask[:,:,z], cmap='jet')
        plt.savefig(os.path.join(path, 'mask_t{}_z{}.png'.format(t, z)))
        plt.clf()

    '''

    ### 2. Same as (1), but for each level

    '''
    path = os.path.join(base_output_path, 'mask-projection-edge')
    create_path(path)

    for t in range(1):
    # for t in range(composite.series.ts):

      mask = np.zeros(composite.series.shape(), dtype=float)
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      gfp = gf(gfp, sigma=2)

      # edge image
      bf_gon = composite.gons.get(channel__name='1', t=t)
      bf = exposure.rescale_intensity(bf_gon.load() * 1.0)
      bf_edge = np.zeros(composite.series.shape())
      for z in range(bf.shape[2]):
        print('loading bf edge... z={}'.format(z))
        bf_slice = bf[:,:,z]
        bf_edge += ft.canny(bf_slice)

      bf_edge = exposure.rescale_intensity(bf_edge * 1.0)

      for r in range(0,composite.series.rs,1):
        for c in range(0,composite.series.cs,1):
          column = scan_point(gfp, r, c)
          print(t,r,c)

          # normalise or pick plot type
          distribution = np.array(column) / np.max(column)

          mask[r,c] = (1.0 - np.mean(distribution)) * bf_edge[r,c]

      # plot
      plt.imshow(mask, cmap='jet')
      plt.savefig(os.path.join(path, 'mask-edge_t{}.png'.format(t)))
      plt.clf()
    '''

    ### 4. Scatter plot of means and standard deviations of normalised gfp distributions
    '''
    path = os.path.join(base_output_path, 'scatter-mean-std')
    create_path(path)
    grid_spacing = 8

    for t in range(1):
    # for t in range(composite.series.ts):
      print('loading gfp...')
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      gfp = gf(gfp, sigma=5)

      # edge image
      bf_gon = composite.gons.get(channel__name='1', t=t)
      bf = exposure.rescale_intensity(bf_gon.load() * 1.0)
      bf_edge = np.zeros(bf.shape)
      for z in range(bf.shape[2]):
        print('loading bf edge... z={}'.format(z))
        bf_slice = bf[:,:,z]
        bf_edge[:,:,z] = ft.canny(bf_slice)

      bf_edge = exposure.rescale_intensity(bf_edge * 1.0)

      for r in range(0,composite.series.rs,grid_spacing):
        for c in range(0,composite.series.cs,grid_spacing):
          column = scan_point(gfp, r, c)

          # normalise or pick plot type
          distribution = np.array(column) / np.max(column)
          z = np.argmax(distribution)
          print(t,r,c,z)

          is_edge = int(bf_edge[r,c,z])==1

          plt.scatter(np.mean(distribution), np.std(distribution), color='b' if is_edge else 'r', s=5 if is_edge else 1)

    # plt.savefig(os.path.join(path, 'mean-std.png'))
    plt.show()
    # plt.clf()
    '''

    ### 5. try subtracting mean field from smoothed gfp
    ''
    path = os.path.join(base_output_path, 'mask-projection-subtract-gfp')
    create_path(path)

    for t in range(1):
    # for t in range(composite.series.ts):

      # mask = np.zeros(composite.series.shape(), dtype=float)
      # gfp_gon = composite.gons.get(channel__name='0', t=t)
      # gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      # gfp = gf(gfp, sigma=2)
      # gfp = exposure.rescale_intensity(gfp * 1.0)
      #
      # for r in range(0,composite.series.rs,1):
      #   for c in range(0,composite.series.cs,1):
      #     column = scan_point(gfp, r, c)
      #     print(t,r,c)
      #
      #     # normalise or pick plot type
      #     distribution = np.array(column) / np.max(column)
      #
      #     mask[r,c] = (1.0 - np.mean(distribution))
      #
      # mask = exposure.rescale_intensity(mask * 1.0)
      #
      # # calculations
      # m = mask.copy()
      # nzm = nonzero_mean_thresholded_preserve(mask)
      # diff = m - nzm.copy()
      # diff = exposure.rescale_intensity(diff * 1.0)

      bf_gon = composite.gons.get(channel__name='1', t=t)
      bf = exposure.rescale_intensity(bf_gon.load() * 1.0)
      bf_edge = ft.canny(bf[:,:,37])

      plt.imshow(bf_edge, cmap='Greys_r')
      plt.savefig(os.path.join(path, 'mask_diff_t{}.png'.format(t)))
      plt.clf()

    ''
