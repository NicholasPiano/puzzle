#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
from apps.img import settings as img_settings

#util
import os
import re
import numpy as np
from scipy.misc import imsave

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. look in each experiments track directories, determine new files
    for series in Series.objects.all():
      # open files in track directory and read lines
      file_list = 
