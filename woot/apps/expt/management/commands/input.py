#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Experiment, Series
from apps.expt.data import *

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--name', # path of images unique to this experiment.
      action='store',
      dest='name',
      default='050714-test',
      help='Path to scan for images'
    ),

    make_option('--base', # defines base search path. All images are in a subdirectory of this directory.
      action='store',
      dest='base',
      default=settings.DATA_ROOT,
      help='Base path on filesystem'
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    # get path
    experiment_name = options['name']
    base_path = os.path.join(options['base'], experiment_name)

    # check if experiment exists
    experiment, exp_created = Experiment.objects.get_or_create(name=experiment_name)
    if exp_created:
      experiment.make_paths(base_path)
      experiment.get_metadata()

    # list directory filtered by allow extension
    storage_file_list = {file_name:experiment.img_path for file_name in os.listdir(experiment.img_path) if os.path.splitext(file_name)[1] in allowed_img_extensions}
    composite_file_list = {file_name:experiment.composite_path for file_name in os.listdir(experiment.composite_path) if os.path.splitext(file_name)[1] in allowed_img_extensions}
    storage_file_list.update(composite_file_list)

    # make paths and series
    for i, (file_name, path) in enumerate(storage_file_list.items()):

      # get template
      template = experiment.templates.get(name='source')
      path, created = template.get_or_create_path(path, file_name)

      print('%s... %s' % (path, 'created.' if created else 'already exists.'))

    # make composites and masks
    # set extent for each series
    for series in experiment.series.all():
      if experiment.allowed_series(series.name):
        if series.rs==-1:
          # rows and columns from image
          (rs,cs) = series.paths.get(channel=series.experiment.channels.all()[0], t=0, z=0).load().shape
          series.rs = rs
          series.cs = cs

          # z and t from counts
          series.zs = series.paths.filter(channel=series.experiment.channels.all()[0], t=0).count()
          series.ts = series.paths.filter(channel=series.experiment.channels.all()[0], z=0).count()

          series.save()

        if series.composites.count()==0:
          series.compose()

        for region_prototype in list(filter(lambda x: x.experiment==experiment.name and x.series==series.name, regions)):
          region, region_created = series.regions.get_or_create(experiment=experiment, name=region_prototype.name)
          if region_created:
            region.description = region_prototype.description
            region.index = region_prototype.index
            region.vertical_sort_index = region_prototype.vertical_sort_index
            region.save()
