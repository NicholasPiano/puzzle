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
import numpy as np
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import matplotlib.pyplot as plt
from scipy.signal import find_peaks_cwt as fpc

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # get gfp gon
    gfp_gon = Gon.objects.get(channel__name='0', t=0, zs__gt=1)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # smooth
    smooth = gf(gfp, sigma=5)

    # get single marker
    marker = Marker.objects.get(composite=gfp_gon.composite, channel=gfp_gon.channel, t=gfp_gon.t, track__track_id=1)

    # generate list of points closest to marker in regular increments, spiral


    # 1. brute force
    chunk_size = 4.0
    # levels = np.zeros((gfp_gon.shape()[0], gfp_gon.shape()[1]), dtype=float)
    for i in range(int(gfp_gon.rs/chunk_size)):
      for j in range(int(gfp_gon.cs/chunk_size)):
        print(i,j)
        r0 = int(i*chunk_size)
        r1 = int(i*chunk_size + chunk_size)
        c0 = int(j*chunk_size)
        c1 = int(j*chunk_size + chunk_size)

        chunk = smooth[r0:r1,c0:c1,:]
        chunk_1D = np.sum(np.sum(chunk, axis=0), axis=0)

        # levels[r0:r1,c0:c1] = np.abs(np.argmax(chunk_1D) - marker.z) # delta z
        # plt.plot(chunk_1D)
        # peaks = fpc(chunk_1D, widths=np.arange(20,21))
        chunk_centre = (r0+int((r1-r0)/2.0), c0+int((c1-c0)/2.0))
        if np.sqrt((chunk_centre[0] - marker.r)**2 + (chunk_centre[1] - marker.c)**2)<20:
          # print(peaks)
          plt.plot(chunk_1D)

    # image = exposure.rescale_intensity(1.0 / (levels + 1.0) * 1.0)

    # plt.imshow(image, cmap='Greys_r')
    plt.show()
