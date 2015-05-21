# expt.command: step03_pmod

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *

# util
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np

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

    # scan
    def scan_point(gfp, r, c, size=3):
      r0 = r - size if r - size >= 0 else 0
      r1 = r + size if r + size <= gfp_gon.rs else gfp_gon.rs
      c0 = c - size if c - size >= 0 else 0
      c1 = c + size if c + size <= gfp_gon.cs else gfp_gon.cs

      column = gfp[r0:r1,c0:c1,:]
      column_1D = np.sum(np.sum(column, axis=0), axis=0)

      return column_1D

    # 1. select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # 2. get single marker and gfp
    for t in range(1):
    # for t in range(composite.series.ts):

      mask = np.zeros(composite.series.shape(), dtype=float)
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
      gfp = gf(gfp, sigma=2)

      for r in range(0,composite.series.rs,1):
        for c in range(0,composite.series.cs,1):
          column = scan_point(gfp, r, c)

          # normalise or pick plot type
          distribution = np.array(column) / np.max(column)

          mask[r,c] = (1.0 - np.mean(distribution))

      plt.imshow(mask)
      plt.show()
