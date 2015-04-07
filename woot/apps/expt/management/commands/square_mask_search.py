#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Gon
from apps.img.util import spiral
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
    marker = Marker.objects.get(composite=gon.composite, channel=gon.channel, t=gon.t, track__track_id=1)

    # generate list of points closest to marker in regular increments, spiral
    # print(spiral())

    # max_values = []
    #
    # for size in range(5,10): # increase mask size
    #   r0 = marker.r - size if marker.r - size >= 0 else 0
    #   r1 = marker.r + size if marker.r + size <= gfp_gon.rs else gfp_gon.rs
    #   c0 = marker.c - size if marker.c - size >= 0 else 0
    #   c1 = marker.c + size if marker.c + size <= gfp_gon.cs else gfp_gon.cs
    #
    #   column = gfp_smooth[r0:r1,c0:c1,:]
    #
    #   column_1D = np.sum(np.sum(column, axis=0), axis=0)
    #
    #   max_values.append(np.argmax(column_1D))
    #
    # marker.z = int(np.mean(max_values))

    # 1. brute force
    chunk_size = 8.0
    levels = np.zeros()
    for i in range(int(gon.rs/chunk_size)):
      for j in range(int(gon.cs/chunk_size)):
        r0 = int(i*chunk_size)
        r1 = int(i*chunk_size + chunk_size)
        c0 = int(j*chunk_size)
        c1 = int(j*chunk_size + chunk_size)

        chunk = smooth[r0:r1,c0:c1,:]
        chunk_1D = np.sum(np.sum(chunk, axis=0), axis=0)
