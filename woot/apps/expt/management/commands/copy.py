#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.expt.data import *
from apps.expt.util import generate_id_token
from apps.img.models import Composite

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
    out = '/Volumes/TRANSPORT/data/puzzle/050714-test/img/region-img/'

    series = Series.objects.get()

    # 1. get time series
    time_set = series.gons.filter(channel__name='1', zs=1, z=30)

    for gon in time_set:
      imsave(os.path.join(out, 'region_%d.tiff' % gon.t), gon.load())
