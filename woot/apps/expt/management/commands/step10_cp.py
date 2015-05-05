#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.expt.data import *
from apps.expt.util import generate_id_token
from apps.img.util import cut_to_black

#util
import os
import re
import subprocess
import numpy as np
from scipy.misc import imsave, imread
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # for each series
    # 1. for each folder in the cp directory, run cell profiler with the given pipeline and the mask folder as output
    for series in Series.objects.all():
      series_cp_path = os.path.join(series.experiment.cp_path, str(series.name))
      for batch_number in os.listdir(series_cp_path):
        # cell profiler input path
        batch_path = os.path.join(series_cp_path, batch_number)

        # output
        output_path = series.experiment.mask_path

        # pipeline path
        pipeline = os.path.join(series.experiment.pipeline_path, os.listdir(series.experiment.pipeline_path)[0])

        # run command
        cmd = '/Applications/CellProfiler.app/Contents/MacOS/CellProfiler -c -r -i {} -o {} -p {} -L DEBUG'.format(batch_path, output_path, pipeline)
        subprocess.call(cmd, shell=True)

        # wait for output
