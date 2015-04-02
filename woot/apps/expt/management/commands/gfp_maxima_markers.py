#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Composite

#util
from scipy.signal import find_peaks_cwt as pks
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
import matplotlib.pyplot as plt
import os

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    out = '/Volumes/TRANSPORT/data/puzzle/050714-test/plot'

    # get gfp gon
    composite = Composite.objects.get()
    gfp_gon = composite.gons.get(channel__name='0', t=0)

    # markers
    markers = composite.series.markers.filter(t=0)

    # load into array
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # smooth
    gfp_smooth = gf(gfp, sigma=5)

    # for each marker, search in the immediate area
    for marker in markers:

      max_values = []

      for size in range(1,10): # increase mask size
        r0 = marker.r - size if marker.r - size >= 0 else 0
        r1 = marker.r + size if marker.r + size <= gfp_gon.rs else gfp_gon.rs
        c0 = marker.c - size if marker.c - size >= 0 else 0
        c1 = marker.c + size if marker.c + size <= gfp_gon.cs else gfp_gon.cs

        column = gfp_smooth[r0:r1,c0:c1,:]

        column_1D = np.sum(np.sum(column, axis=0), axis=0)

        max_values.append(np.argmax(column_1D))

      print(int(np.mean(max_values)))
