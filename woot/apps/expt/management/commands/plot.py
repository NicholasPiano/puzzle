#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import Cell, CellInstance

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
    # details

    speeds = {}
    for ci in CellInstance.objects.all():
      if ci.region in speeds:
        speeds[ci.region].append(ci.velocity())
      else:
        speeds[ci.region] = [ci.velocity()]

    for key, value in speeds.items():
      print(key, np.mean(value))

    # total displacement over total time
      # for each cell
      # total displacement in region over total region time

    # absolute magnitude of average velocity

    # 
