# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *
from apps.expt.data import *
from apps.img.util import nonzero_mean, cut_to_black, create_bulk_from_image_set

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

    # 1. select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # 2. Call pmod mod
    mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_step13_cell_masks')

    # 3. Run mod
    print('step13 | processing mod_step13_cell_masks...', end='\r')
    mod.run()
    print('step13 | processing mod_step13_cell_masks... done.'
