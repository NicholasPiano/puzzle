#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.cell.models import Experiment
from apps.img import settings as img_settings
from apps.img.models import SourceImage, Composite

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    #1. for each composite, check if chunk creation is pending (for now - has chunks?)
    #2. call chunkify
    c = Composite.objects.get()
    c.chunkify()
