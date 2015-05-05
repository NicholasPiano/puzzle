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

    for c in Cell.objects.all():
      plt.plot([ci.t for ci in c.cell_instances.order_by('t')],[ci.z for ci in c.cell_instances.order_by('t')])

    plt.show()
