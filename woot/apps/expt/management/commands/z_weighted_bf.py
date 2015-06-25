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

def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

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
    output_dir = '/Volumes/Extra/test'
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    t=0

    Z = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_z_t0.tiff')) * 1.0)
    mean = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_mean_t0.tiff')) * 1.0)

    bf_gon = composite.gons.get(t=t, channel__name='1')
    bf = bf_gon.load()
    bf = exposure.rescale_intensity(bf * 1.0)

    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)
    gfp = gf(gfp, sigma=2)

    # rescale Z
    Z = (Z * (series.zs-1) - 8).astype(int)

    # for each pixel in weighted image, choose the value from the brightfield at that level
    weighted_img = np.zeros(series.shape(d=2))

    for r in range(series.rs):
      for c in range(series.cs):
        print(r,c)
        weighted_img[r,c] = bf[r,c,Z[r,c]]

    # final = weighted_img * (1.0 - mean)

    # imsave(os.path.join(output_dir, 'final_mod.png'), final)

    plt.imshow(weighted_img, cmap='Greys_r')
    plt.show()
