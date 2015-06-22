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
    t = 0
    markers = series.markers.filter(t=t)
    image_template = os.path.join(output_dir, '{}_s{}_ch-{}_t{}_z{}_m{}.tiff') # expt, series, channel, t, z, marker

    # load gfp
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)

    gfp_temp = gfp.copy()
    for i in range(gfp.shape[2]):
      slice = gfp[:,:,i]
      slice_gf = gf(slice, sigma=3)
      gfp_temp[:,:,i] = slice_gf

    gfp = gfp_temp.copy()

    # marker
    # marker = series.markers.filter(r__gt=350, c__gt=100, c__lt=200, t=t)
    #
    # for m in marker:
    #   print(m.r, m.c, m.pk)

    marker = series.markers.get(pk=305)

    r, c = 100, 100
    # print(r,c)

    for radius in range(1,30,2):
      d = scan_point(gfp, series.rs, series.cs, r, c, size=radius)
      plt.plot(d, label='r={}'.format(radius))

    plt.legend()
    plt.show()
