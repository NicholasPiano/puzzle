#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import CellInstance as C

#util
import os
import re

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):

    plot_path = '/Volumes/transport/data/puzzle/050714-test/plot/'

    for c in C.objects.filter(region=4):
      pass
