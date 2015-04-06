#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.expt.data import *

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
    # 1. input masks for each series
    for series in Series.objects.all():
      file_list = [file_name for file_name in os.listdir(series.experiment.mask_path) if os.path.splitext(file_name)[1] in allowed_img_extensions]

      mask_template = series.experiment.templates.get(name='cp')

      for file_name in file_list:
        print(mask_template.dict(file_name))
