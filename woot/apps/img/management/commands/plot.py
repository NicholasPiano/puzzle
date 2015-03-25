#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import CellInstance as C

#util
import os
import re
from optparse import make_option
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):

    a_r1 = []
    a_r4 = []
    v_r1 = []
    v_r4 = []

    for c in C.objects.filter(region=1):
      a_r1.append(c.area())
      v_r1.append(c.velocity())

    for c in C.objects.filter(region=4):
      a_r4.append(c.area())
      v_r4.append(c.velocity())


    # histograms
    
