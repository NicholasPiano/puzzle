#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Gon
from apps.cell.models import Marker

#util
import os
import re
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # get gfp gon
    gon = Gon.objects.get(channel__name='0', t=0, zs__gt=1)
    gfp = exposure.rescale_intensity(gon.load() * 1.0)

    # smooth
    smooth = gf(gfp, sigma=5)

    # get single marker
    marker = Marker.objects.get()
