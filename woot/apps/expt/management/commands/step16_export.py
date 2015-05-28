# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option

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

    # output
    output_file = os.path.join(series.experiment.data_path, 'output_{}_s{}.csv'.format(series.experiment.name, series.name))

    with open(output_file, 'w+') as f:
      print('experiment, series, cell id, ')
      for cell in series.cells.order_by('pk'):
        for cell_instance in cell.cell_instances.order_by('t'):
          print(cell_instance.line(), end='')
          # f.write(cell_instance.line())
