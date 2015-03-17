#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Composite, Mod
from apps.img import settings as img_settings

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    c = Composite.objects.get()
    pmod = c.mods.create(experiment=c.experiment, series=c.series, id_token=img_settings.generate_id_token(Mod), algorithm='pmod_track')
    pmod.run()
