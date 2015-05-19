# expt.command: search_masks

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *
from apps.expt.data import *
from apps.img.util import nonzero_mean, cut_to_black

# util
import os
import numpy as np
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
from scipy.misc import imsave

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
    > Search vertically inside each mask and determine what level it lies at

    2. What data structures are input?
    > Mask, Gon

    3. What data structures are output?
    > Channel, Gon, Mask

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    '''

    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    output_path = '/Volumes/transport/demo/plots/plot.png'

    for t in range(series.ts):
      mask_gon_set = composite.gons.filter(channel__name__in=['pmodreduced','bfreduced'], template__name='cp', t=t)

      # load gfp
      gfp_gon = composite.gons.get(channel__name='0', t=t)
      smooth_gfp = gf(exposure.rescale_intensity(gfp_gon.load() * 1.0), sigma=0)

      for i,mask_gon in enumerate(mask_gon_set):
        mask_array = mask_gon.load()

        for unique_id in [u for u in np.unique(mask_array) if u>0]:
          # get mask
          mask = mask_array==unique_id

          # cut to black to save time
          cut_mask, (r,c,rs,cs) = cut_to_black(mask)

          # smaller masked array
          mini_masked_array = np.ma.array(smooth_gfp[r:r+rs, c:c+cs, :], mask=np.dstack([np.invert(cut_mask)]*smooth_gfp.shape[2]), fill_value=0)

          # squeeze into column
          column = np.sum(np.sum(mini_masked_array, axis=0), axis=0)

          # details
          max_z = np.argmax(column)

          for marker in series.markers.filter(t=t):
            if marker.r > r and marker.r < r + rs and marker.c > c and marker.c < c + cs:
              print(t, i, unique_id, 'mark')
              plt.plot(column, color='r')
            else:
              plt.plot(column, color='b')

    plt.savefig(output_path)
