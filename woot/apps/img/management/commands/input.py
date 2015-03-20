#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--path', # path of images unique to this experiment.
      action='store',
      dest='path',
      default='050714',
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
    experiment_name = options['path']
    base_path = os.path.join(options['base'], experiment_name)

    # check if experiment exists
    experiment, exp_created = Experiment.objects.get_or_create(name=experiment_name)
    if exp_created:
      experiment.make_paths(base_path)


    # list directory filtered by allow extension
