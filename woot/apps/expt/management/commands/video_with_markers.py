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

    for t in range(series.ts):
      # 1. get central image in the brightfield for each timestep
      bf_gon = series.composites.get().gons.get(channel__name='1', t=t).gons.get(z=int(series.zs/2.0))
      bf = bf_gon.load()

      # 2. get region image for this frame, outline in white and superimpose
      region_gon = series.composites.get().gons.get(channel__name='-regions', t=t)
      regions = region_gon.load()
      regions_lines = (regions==0).astype(int) * 255

      bf_with_regions = 0.2 * regions_lines + 0.8 * bf
      plt.imshow(bf_with_regions, cmap='Greys_r')

      # 3. for each cell instance in the frame, marker a dot at its position and write the id, r, c, and region
      cell_instances = series.cell_instances.filter(t=t)
      for cell_instance in cell_instances:
        # add dot at cell instance centre position
        plt.scatter(cell_instance.c, cell_instance.r, color='red', s=5)
        plt.text(cell_instance.c+5, cell_instance.r+5, '{}'.format(cell_instance.cell.pk), fontsize=8, color='white')

        # add text at position offset

      plt.text(-50, -50, 'expt={} series={} t={}'.format(series.experiment.name, series.name, t), fontsize=15, color='black')
      plt.savefig(os.path.join(series.experiment.tracking_path, 'tracking_t{}.png'.format(t)), dpi=100)
      plt.cla()
