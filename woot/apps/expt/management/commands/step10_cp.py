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
