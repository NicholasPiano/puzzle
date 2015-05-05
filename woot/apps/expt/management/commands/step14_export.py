#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.cell.models import CellInstance

#util
import os
import re
import numpy as np
from scipy.misc import imsave
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    for series in Series.objects.all():
      output_filename = os.path.join(series.experiment.data_path, 'output_{}_s{}.csv'.format(series.experiment.name, series.name))

      with open(output_filename, 'w') as output_file:
        output_file.write('cell_id, t, row, column, Z, row_velocity, column_velocity, Z_velocity, area, region\n')
        for cell_instance in CellInstance.objects.order_by('t', 'cell__cell_id'):
          line = cell_instance.raw_line()
          output_file.write(line)
