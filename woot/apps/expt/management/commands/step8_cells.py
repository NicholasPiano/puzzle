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
    out = '/Volumes/TRANSPORT/data/puzzle/050714/img/output/'

    # 1. get composite
    c = Composite.objects.get()

    # 2. get marker
    for m in c.markers.all():

      # 3. get masks
      black = m.combined_mask()

      plt.imshow(black)
      plt.savefig(os.path.join(out, 'mask_%d' % m.pk))
