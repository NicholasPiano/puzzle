# expt.command: step10_cp

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *
from apps.expt.data import allowed_img_extensions

# util
import os
import subprocess
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
    > Remotely run CellProfiler using a command line. I want to pretend that I am simply modding the images and creating a new channel.

    2. What data structures are input?
    > CP Pipeline file, Channel

    3. What data structures are output?
    > Nothing

    4. Is this stage repeated/one-time?
    > One-time per pipeline

    Steps:

    1. Search in pathfor batches
    2. For each batch, run command

    '''

    # 1. get path and batches
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])

    series_cp_path = os.path.join(series.experiment.cp2_path, series.name)
    for batch_number in os.listdir(series_cp_path):
      # cell profiler input path
      batch_path = os.path.join(series_cp_path, batch_number)

      # output
      output_path = os.path.join(series.experiment.output_path, series.name, batch_number)

      if not os.path.exists(output_path):
        os.makedirs(output_path)

      # pipeline path
      pipeline = os.path.join(series.experiment.pipeline_path, 'cell_mask_v0.1.cppipe')

      # run command
      cmd = '/Applications/CellProfiler.app/Contents/MacOS/CellProfiler -c -r -i {} -o {} -p {}'.format(batch_path, output_path, pipeline)
      subprocess.call(cmd, shell=True)
