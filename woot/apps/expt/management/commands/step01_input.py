# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.expt.data import *

# util
import os
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
    > Converts image file names into searchable pixel space composite

    2. What data structures are input?
    > strings

    3. What data structures are output?
    > Experiment, Series, Path, Channel, Composite

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. check if experiment name is in the base folder
    2. create a new experiment
    3. create a new series
    4. for each path in experiment folder, make a path object.
      - if path object matches the series, keep it, else delete
    5. make composite from series

    '''

    # vars
    base_path = settings.DATA_ROOT
    expt_name = options['expt']
    series_name = options['series']
    expt_path = os.path.join(base_path, expt_name)

    # time
    # start

    # 1. check experiment name in base folder
    if os.path.exists(expt_path):
      # 2. create new experiment
      expt, expt_created = Experiment.objects.get_or_create(name=expt_name)

      if expt_created:
        expt.make_paths(os.path.join(base_path, expt_name))
        expt.get_metadata()

      # 3. create new series
      if expt.allowed_series(series_name):
        series, series_created = expt.series.get_or_create(name=series_name)

        # 4. for each path in the expt folder, create new path if the series matches.
        for root in expt.img_roots():

          img_files = [f for f in os.listdir(root) if os.path.splitext(f)[1] in allowed_img_extensions]
          number_img_files = len(img_files)

          if number_img_files>0:
            for i, file_name in enumerate(img_files):

              path, path_created, path_message = expt.get_or_create_path(series, root, file_name)
              print('step01 | finding new image files in {}: ({}/{}) {} ...path {}'.format(root, i+1, number_img_files, file_name, path_message), end=('\n' if i==number_img_files-1 else '\r'))

          else:
            print('step01 | no files found in {}'.format(root))

        # 5. measurements
        if series.rs==-1: # series has not had its size set
          print('step01 | setting measurements for {} series {}'.format(expt.name, series.name))

          # rows and columns from image
          (rs,cs) = series.paths.get(channel=series.experiment.channels.get(name='0'), t=0, z=0).load().shape
          series.rs = rs
          series.cs = cs

          # z and t from counts
          series.zs = series.paths.filter(channel=series.experiment.channels.get(name='0'), t=0).count()
          series.ts = series.paths.filter(channel=series.experiment.channels.get(name='0'), z=0).count()

          series.save()

        else:
          print('step01 | measurements already set for {} series {}'.format(expt.name, series.name))

        # 6. compose
        if series.composites.count()==0:
          print('step01 | composing {} series {}... '.format(expt.name, series.name), end='\r')
          series.compose()
          print('step01 | composing {} series {}... done.                                      '.format(expt.name, series.name), end='\n')
        else:
          print('step01 | {} series {} already composed.'.format(expt.name, series.name))

        # 7. add to composite
        print('step01 | checking for additions to current composite...')

        # get current composite id

        # compose channels

        # 8. set regions
        print('step01 | creating regions for {} series {}... '.format(expt.name, series.name), end='\r')
        for region_prototype in list(filter(lambda rp: rp.experiment==expt.name and rp.series==series.name, regions)):
          region, region_created = series.regions.get_or_create(experiment=expt, name=region_prototype.name)
          if region_created:
            region.description = region_prototype.description
            region.index = region_prototype.index
            region.vertical_sort_index = region_prototype.vertical_sort_index
            region.save()
        print('step01 | creating regions for {} series {}... done.'.format(expt.name, series.name), end='\n')

      else:
        print('step01 | not a valid series: {}.{}'.format(expt_name, series_name))

    else:
      print('step01 | experiment not in base folder: {}'.format(base_path))
