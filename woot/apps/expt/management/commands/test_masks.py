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
    marker = Marker.objects.get(pk=26)

    # get combiend mask
    combined_mask = marker.combined_mask()

    print(np.sum(combined_mask>0) * marker.experiment.rmop * marker.experiment.cmop)

    plt.imshow(combined_mask)
    plt.show()
