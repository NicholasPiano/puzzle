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
import matplotlib.patches as patches
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

    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)
    gfp = gf(gfp, sigma=2)

    gfp = gfp[380:480,380:480,:]

    r, c = 65, 45
    rs, cs = 100, 100

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # ax.imshow(np.sum(gfp, axis=2), cmap='Greys_r')

    # patches
    # ax.scatter(c,r,color='blue')

    colours = ['blue','green', 'red', 'cyan', 'magenta']
    for i, size in enumerate(list(range(0,20,4))):
      # ax.add_patch(
      #   patches.Rectangle(
      #     (c-size/2.0, r-size/2.0),
      #     size,
      #     size,
      #     fill=False,
      #     edgecolor=colours[i]
      #   )
      # )

      distribution = scan_point(gfp, rs, cs, r, c, size=size)
      ax.plot(distribution / np.max(distribution), label='r={}'.format(size))
      # ax.plot(distribution)

    ax.set_ylabel('normalised intensity', fontsize=24)
    ax.set_xlabel('Z slice', fontsize=24)
    fig.suptitle('GFP profile in z with constant x,y', fontsize=24)
    plt.legend()
    plt.show()
