#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import Marker

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
    # get marker
    marker = Marker.objects.get(pk=13)

    # get combiend mask
    combined_mask = marker.combined_mask()

    masked = np.ma.array(combined_mask, mask=combined_mask==0)
    print(masked.sum() / masked.max())

    # plt.imshow(combined_mask)
    # plt.show()
