#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import Cell

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # cells

    for cell in Cell.objects.all():
      cell.velocities()
