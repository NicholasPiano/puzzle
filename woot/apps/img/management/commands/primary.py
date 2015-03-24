#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.pix.models import Composite, Mod
from apps.img import settings as img_settings

#util
import os
import re
from optparse import make_option
import matplotlib.pyplot as plt
from skimage import feature as ft
from skimage import exposure as ex
from scipy.ndimage.filters import gaussian_filter as gaufil
from scipy.misc import imsave

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    c = Composite.objects.get()

    m = c.mods.create(id_token=c.generate_mod_id(), algorithm='primary')
    m.run()
