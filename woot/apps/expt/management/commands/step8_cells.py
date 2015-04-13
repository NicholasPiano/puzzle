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
    # 1. get composite
    c = Composite.objects.get()

    # 2. get marker
    m = c.markers.get(pk=5)

    # 3. get masks
    secondary_mask_set = m.secondary_mask_set()

    black = np.zeros((512,512), dtype=float)

    for mask in secondary_mask_set:
      black += mask.load().astype(float) * 1.0/(1.0 + abs(m.z - mask.gon.z))

    black[black<np.ma.array(black, mask=black==0).mean()] = 0

    plt.imshow(black)
    plt.show()
