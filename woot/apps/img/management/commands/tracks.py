#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
from apps.img import settings as img_settings

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    track_file_template = r'(?P<experiment>.+)_s(?P<series>.+)_i(?P<index>.+)\.xls'

    # 1. look in each experiments track directories, determine new files
    for experiment in Experiment.objects.all():
      track_path = os.path.join(experiment.base_path, experiment.track_path)

      # file_list =

    # 2. open each new file, add lines to cell markers
