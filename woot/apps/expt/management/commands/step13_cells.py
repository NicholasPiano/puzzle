# expt.command: step11_reduced

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
from scipy.misc import imsave
from scipy.ndimage.measurements import center_of_mass as cm
from scipy.ndimage.morphology import distance_transform_edt as dt
from scipy.ndimage.morphology import binary_erosion as be

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
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    for t in range(1):
      # load entire set of mask gons as 3D box with accessor dictionary
      mask_gon_stack = None
      mask_accessor_dict = {}

      mask_gon_set = composite.gons.filter(channel__name='bfreduced', t=t)

      for i, mask_gon in enumerate(mask_gon_set):
        m = mask_gon.load()
        mask_accessor_dict[mask_gon.pk] = i
        if mask_gon_stack is None:
          mask_gon_stack = m
        else:
          mask_gon_stack = np.dstack([mask_gon_stack, m])

      def slice(z=None, pk=None):
        if z is None:
          return mask_gon_stack[:,:,mask_accessor_dict[pk]]
        else:
          return mask_gon_stack[:,:,mask_accessor_dict[mask_gon_set.get(z=z).pk]]

      # to access a single mask in the bulk, need (gon.pk or gon.z, unique_id)
      for z in range(series.zs):
        # full_mask = np.zeros(series.shape(), dtype=int)
        mask_set = list(composite.masks.filter(max_z=z, gon__t=t, gon__channel__name='bfreduced'))
        for mask in mask_set:
          print(mask.pk)
          # full_mask += (slice(pk=mask.gon.pk)==mask.mask_id).astype(int)

        # imsave(os.path.join(series.experiment.output_path, 'level_{}.tiff'.format(z)), full_mask)
