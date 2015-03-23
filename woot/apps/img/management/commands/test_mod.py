#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.pix.models import Composite, Mod

#util
import os
import re

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    c = Composite.objects.get()

    m = c.mods.create(id_token=c.generate_mod_id(), algorithm='channel_test_3D')
    m.run()
