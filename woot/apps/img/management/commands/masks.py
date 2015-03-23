#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
from apps.img.settings import *

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
    # for each series, gather masks
