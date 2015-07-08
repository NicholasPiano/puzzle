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
import shutil as sh

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

    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    output_path = os.path.join(series.experiment.img_path, 'bf')

    for t in range(series.ts):
      bf_gon = composite.gons.get(channel__name='1', t=t)
      slice = bf_gon.gons.get(z=37)

      from_path = slice.paths.get().url
      to_path = os.path.join(output_path, slice.paths.get().file_name)
      sh.copy2(from_path, to_path)
      print(t)
