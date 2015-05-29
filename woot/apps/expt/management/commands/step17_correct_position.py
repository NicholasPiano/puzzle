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

    # correct positions and then velocities
    # true R = CI.c + CI.gon.r
    # true C = CI.r + CI.gon.c
    for cell_instance in series.cell_instances.all():
      cell_instance.r = cell_instance.c + cell_instance.gon.r
      cell_instance.c = cell_instance.r + cell_instance.gon.c
      cell_instance.save()

    # 3. calculate cell velocities
    for cell in series.cells.all():
      previous_cell_instance = None
      for cell_instance in cell.cell_instances.order_by('t'):
        if previous_cell_instance is not None:
          cell_instance.vr = cell_instance.r - previous_cell_instance.r
          cell_instance.vc = cell_instance.c - previous_cell_instance.c
          cell_instance.vz = cell_instance.z - previous_cell_instance.z
        else:
          cell_instance.vr = 0
          cell_instance.vc = 0
          cell_instance.vz = 0

        previous_cell_instance = cell_instance

        cell_instance.save()
